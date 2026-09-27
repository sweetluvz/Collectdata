# Collectdata — Thu thập dữ liệu nghiên cứu tự động

Hệ thống thu thập dữ liệu định kỳ bằng **GitHub Actions** (không cần máy chủ riêng) cho ba nhóm dữ liệu nghiên cứu:

| Nhóm | Mục đích nghiên cứu | Nguồn |
|---|---|---|
| **Năng lượng & môi trường** | Dự báo phụ tải ngắn hạn (STLF), dự báo công suất gió/mặt trời, mô hình không–thời gian | Open-Meteo, EIA-930 (Mỹ), ENTSO-E (châu Âu) |
| **Bất động sản** | Định giá hedonic, phân tích không gian, tác động hạ tầng | batdongsan.com.vn, Zillow Research |
| **Bằng sáng chế** | Dự báo công nghệ mới nổi, phân tích hội tụ công nghệ (mạng CPC) | USPTO PatentsView, Lens.org (gồm WIPO/EP/US) |

Mỗi lần chạy, dữ liệu mới được **gộp (upsert)** vào các file CSV theo tháng trong thư mục `data/`, rồi bot tự commit và push lại vào repo.

---

## Mục lục

1. [Kiến trúc](#1-kiến-trúc)
2. [Lịch chạy](#2-lịch-chạy)
3. [Cài đặt lần đầu](#3-cài-đặt-lần-đầu)
4. [Cấu trúc dữ liệu](#4-cấu-trúc-dữ-liệu)
5. [Từ điển dữ liệu](#5-từ-điển-dữ-liệu-data-dictionary)
6. [Chạy thủ công & backfill dữ liệu lịch sử](#6-chạy-thủ-công--backfill-dữ-liệu-lịch-sử)
7. [Chạy trên máy cá nhân](#7-chạy-trên-máy-cá-nhân)
8. [Đọc dữ liệu để phân tích](#8-đọc-dữ-liệu-để-phân-tích)
9. [Giám sát & bảo trì](#9-giám-sát--bảo-trì)
10. [Tuỳ biến](#10-tuỳ-biến)
11. [Giới hạn & rủi ro đã biết](#11-giới-hạn--rủi-ro-đã-biết)

---

## 1. Kiến trúc

```
GitHub Actions (cron)
  │
  ├── collect_energy.yml      ── 6 giờ/lần ──▶ scrapers/energy/*      ──▶ data/energy/...
  ├── collect_realestate.yml  ── hằng ngày ──▶ scrapers/realestate/*  ──▶ data/realestate/...
  ├── collect_patents.yml     ── hằng tuần ──▶ scrapers/patents/*     ──▶ data/patents/...
  ├── keepalive.yml           ── hằng tuần ──▶ bật lại các workflow (tránh bị GitHub tự tắt)
  └── ci.yml                  ── mỗi push   ──▶ pytest (không chạy khi chỉ data/ thay đổi)

Mỗi collector:  gọi API/HTML ──▶ chuẩn hoá DataFrame ──▶ utils/storage.upsert()
                                                              │
                              data/<nhóm>/<nguồn>/<bảng>/YYYY-MM.csv[.gz]
                                                              │
scripts/commit_data.sh <nhóm>:  build CATALOG.md ──▶ git commit ──▶ pull --rebase ──▶ push
```

```
.
├── .github/workflows/        # lịch chạy & CI
├── scrapers/
│   ├── energy/               # weather_collector, eia_collector, entsoe_collector
│   ├── realestate/           # batdongsan_collector, zillow_collector
│   └── patents/              # uspto_collector, lens_collector, common.py (danh sách mã CPC)
├── utils/
│   ├── http.py               # session có retry/backoff, check() lỗi API, đọc biến môi trường
│   └── storage.py            # upsert theo tháng, ghi file chỉ khi nội dung thay đổi
├── scripts/
│   ├── commit_data.sh        # commit + push an toàn khi nhiều workflow chạy đồng thời
│   └── build_catalog.py      # sinh data/<nhóm>/CATALOG.md
├── tests/                    # pytest, mock HTTP — không gọi mạng
└── data/                     # dữ liệu (bot tự cập nhật)
```

### Các nguyên tắc thiết kế

- **Upsert với cửa sổ chồng lấn:** mỗi lần chạy lấy lại vài ngày gần nhất. Nhờ vậy, nếu một lần cron bị trễ hoặc lỗi thì lần sau tự lấp khoảng trống, và các giá trị được nguồn sửa lại sau (EIA-930 thường sửa số liệu trong vài ngày) sẽ ghi đè bản cũ theo khoá chính.
- **Phân vùng theo tháng:** mỗi bảng là một thư mục, mỗi tháng một file. File nhỏ, dễ đọc từng phần, và git diff chỉ chạm vào tháng có thay đổi.
- **Ghi file chỉ khi nội dung đổi:** file `.gz` được nén với `mtime=0` nên dữ liệu giống nhau cho ra byte giống nhau, nhờ đó git không lưu thêm bản sao mới nếu dữ liệu không đổi.
- **Mỗi workflow chỉ ghi vào thư mục nhóm của mình**, nên khi hai workflow push gần nhau, `pull --rebase` không bao giờ xung đột.
- **Một nguồn lỗi không làm mất nguồn khác:** các bước sau vẫn chạy (`if: !cancelled()`), bước commit vẫn lưu phần đã thu được, và job được đánh dấu *failed* để GitHub gửi email cảnh báo.
- **Thiếu API key thì bỏ qua (exit 0) kèm cảnh báo**, không làm hỏng cả workflow.
- **Mọi thời gian lưu theo UTC**, định dạng `YYYY-MM-DDTHH:MMZ`.

---

## 2. Lịch chạy

| Workflow | Cron (UTC) | Giờ Việt Nam | Cửa sổ dữ liệu mỗi lần chạy |
|---|---|---|---|
| `collect_energy.yml` | `23 */6 * * *` | 06:23, 12:23, 18:23, 00:23 | Open-Meteo 3 ngày quá khứ + 2 ngày dự báo; EIA 7 ngày; ENTSO-E 3 ngày + 1 ngày tới |
| `collect_realestate.yml` | `37 1 * * *` | 08:37 hằng ngày | 5 trang × 6 danh mục Batdongsan; tối đa 80 trang chi tiết mới |
| `collect_patents.yml` | `11 3 * * 3` | 10:11 thứ Tư | PatentsView 180 ngày; Lens 14 ngày |
| `keepalive.yml` | `0 6 * * 1` | 13:00 thứ Hai | — |

**Vì sao năng lượng chạy 6 giờ/lần mà không phải mỗi giờ?** Dữ liệu vẫn có độ phân giải giờ (hoặc 15 phút với ENTSO-E); chỉ tần suất *gọi API* là 6 giờ. Vì mỗi lần lấy lại cả cửa sổ nhiều ngày nên không mất giờ nào. Chạy mỗi giờ sẽ tốn khoảng 720 lượt/tháng; với repo **private**, số phút miễn phí của GitHub Actions có hạn nên dễ vượt hạn mức khi cộng các workflow khác. Riêng bảng dự báo thời tiết thì chạy dày hơn sẽ có nhiều "phiên bản dự báo" hơn; có thể đổi cron nếu cần.

> GitHub **không đảm bảo** cron chạy đúng phút; lúc tải cao có thể trễ vài chục phút hoặc bỏ lượt. Cửa sổ chồng lấn ở trên sinh ra để bù cho điều này.

---

## 3. Cài đặt lần đầu

### 3.1. Nhánh mặc định

Cron **chỉ chạy trên nhánh mặc định** của repo. Hiện nhánh mặc định là `claude/upbeat-cori-snhhva`. Nên tạo `main` từ nhánh này rồi đặt làm mặc định:
*Settings → General → Default branch*.

### 3.2. Quyền ghi của Actions

*Settings → Actions → General*:
- **Actions permissions:** Allow all actions.
- **Workflow permissions:** các workflow đã tự khai báo `contents: write`. Nếu tổ chức giới hạn quyền của token ở mức read-only thì cần chọn **Read and write permissions**.

### 3.3. API key (Secrets)

Vào *Settings → Secrets and variables → Actions → New repository secret*. Chỉ cần thêm key cho nguồn bạn dùng; nguồn nào thiếu key sẽ được bỏ qua.

| Secret | Nguồn | Cách lấy | Ghi chú |
|---|---|---|---|
| *(không cần)* | Open-Meteo | — | Miễn phí cho mục đích phi thương mại, giới hạn ~10.000 lượt/ngày |
| *(không cần)* | Batdongsan, Zillow Research | — | |
| `EIA_API_KEY` | EIA Open Data | Đăng ký tại <https://www.eia.gov/opendata/register.php>, key gửi qua email ngay | Miễn phí |
| `ENTSOE_API_KEY` | ENTSO-E Transparency | (1) Tạo tài khoản tại <https://transparency.entsoe.eu>; (2) gửi email tới `transparency@entsoe.eu`, tiêu đề *"Restful API access"*, nêu email tài khoản; (3) khi được duyệt, vào *My Account Settings → Generate token* | Thường mất vài ngày làm việc |
| `PATENTSVIEW_API_KEY` | USPTO PatentsView | Gửi yêu cầu API key qua cổng hỗ trợ PatentsView (<https://patentsview.org> → *API*) | Miễn phí, giới hạn 45 request/phút |
| `LENS_API_TOKEN` | Lens.org | Tạo tài khoản, vào <https://www.lens.org/lens/user/subscriptions> để xin quyền **Patent API** (có gói trial/học thuật) | Cần mô tả mục đích sử dụng |

### 3.4. Chạy thử

*Actions → chọn workflow → Run workflow*. Chạy lần lượt cả ba, sau đó kiểm tra:
- log từng bước (có `::warning::` hay không);
- file `data/<nhóm>/CATALOG.md` đã có bảng và số dòng chưa.

> Code đã được test với mock (`tests/`), nhưng **chưa được chạy với API thật**. Nếu lần chạy đầu có lỗi, thường là do tên trường API hoặc CSS selector; thông báo lỗi sẽ in ra phần thân phản hồi của API (không lộ API key) để sửa.

---

## 4. Cấu trúc dữ liệu

```
data/
├── energy/
│   ├── CATALOG.md
│   ├── weather/
│   │   ├── observed/YYYY-MM.csv          # thời tiết theo giờ (giá trị mới nhất mỗi giờ)
│   │   └── forecast/YYYY-MM.csv          # MỌI bản dự báo, theo thời điểm phát hành (issued_at)
│   ├── airquality/observed/YYYY-MM.csv   # PM2.5, PM10, NO2, O3, SO2, CO, US AQI
│   ├── eia/
│   │   ├── region/YYYY-MM.csv            # phụ tải, dự báo phụ tải, phát điện ròng, trao đổi liên vùng
│   │   └── fuel_type/YYYY-MM.csv         # phát điện theo loại nhiên liệu
│   └── entsoe/
│       ├── load/YYYY-MM.csv
│       ├── load_forecast/YYYY-MM.csv
│       ├── generation/YYYY-MM.csv
│       ├── wind_solar_forecast/YYYY-MM.csv
│       └── day_ahead_price/YYYY-MM.csv
├── realestate/
│   ├── CATALOG.md
│   ├── batdongsan/
│   │   ├── listings/YYYY-MM.csv          # ảnh chụp hằng ngày: 1 dòng / (tin đăng, ngày)
│   │   └── details/YYYY-MM.csv           # 1 dòng / tin đăng: toạ độ, mô tả, thông số
│   └── zillow/
│       ├── zhvi_metro/YYYY-MM.csv.gz     # mỗi file = 1 bản phát hành (dạng rộng)
│       ├── zhvi_county/YYYY-MM.csv.gz
│       └── zori_metro/YYYY-MM.csv.gz
└── patents/
    ├── CATALOG.md
    ├── uspto/grants/YYYY-MM.csv.gz       # theo tháng cấp bằng
    └── lens/publications/YYYY-MM.csv.gz  # theo tháng công bố
```

Quy ước:
- **Tên file = tháng của cột thời gian** trong bảng, không phải tháng thu thập. Riêng bảng `forecast` phân vùng theo `issued_at`, còn `listings` theo `scraped_at`.
- **File `.csv.gz`** dùng cho dữ liệu văn bản lớn (sáng chế) và bản phát hành Zillow. `pandas.read_csv` đọc trực tiếp được.
- **Giá trị rỗng** được lưu thành chuỗi rỗng.
- **`CATALOG.md`** của mỗi nhóm liệt kê từng bảng: số file, số dòng, cột thời gian, mốc đầu/cuối, dung lượng. Đây là chỗ nhanh nhất để kiểm tra dữ liệu có đang được cập nhật đều hay không.

---

## 5. Từ điển dữ liệu (data dictionary)

> Tên cột của EIA, ENTSO-E, PatentsView và Lens do API trả về. Danh sách dưới đây viết theo tài liệu API và cần đối chiếu lại sau lần chạy thật đầu tiên.

### 5.1. `energy/weather/observed` & `energy/weather/forecast`

| Cột | Ý nghĩa |
|---|---|
| `location` | Mã điểm, dạng `<quốc gia>_<vùng lưới>_<thành phố>`, ví dụ `US_ERCO_Houston`, `DE_Berlin`, `VN_HoChiMinh` |
| `issued_at` | *(chỉ ở forecast)* thời điểm lấy bản dự báo (UTC, làm tròn xuống giờ) |
| `time` | Giờ hiệu lực (UTC) |
| `temperature_2m`, `apparent_temperature`, `dew_point_2m` | °C |
| `relative_humidity_2m` | % |
| `precipitation` | mm |
| `cloud_cover` | % |
| `surface_pressure` | hPa |
| `wind_speed_10m`, `wind_speed_100m`, `wind_gusts_10m` | km/h (độ cao 100 m sát với chiều cao hub turbine) |
| `wind_direction_100m` | độ |
| `shortwave_radiation`, `direct_normal_irradiance`, `diffuse_radiation` | W/m² (GHI, DNI, DHI — đầu vào cho dự báo điện mặt trời) |

`observed` là giá trị phân tích/mô hình của Open-Meteo trong vài ngày gần nhất, **không phải số đo trạm**. Khi cần dữ liệu tái phân tích chuẩn (ERA5) cho bài báo, có thể tải lại từ Open-Meteo Historical API.

`forecast` lưu **mọi phiên bản dự báo**. Nhờ vậy mô hình STLF có thể được đánh giá bằng đúng thông tin thời tiết có sẵn tại thời điểm dự báo, thay vì dùng thời tiết thực tế làm đầu vào (cách này làm kết quả lạc quan hơn thực tế).

### 5.2. `energy/airquality/observed`
`location`, `time`, `pm10`, `pm2_5` (µg/m³), `nitrogen_dioxide`, `ozone`, `sulphur_dioxide`, `carbon_monoxide` (µg/m³), `us_aqi`.

### 5.3. `energy/eia/region` & `energy/eia/fuel_type`

| Cột | Ý nghĩa |
|---|---|
| `period` | Giờ (UTC) |
| `respondent`, `respondent-name` | Vùng cân bằng (balancing authority): `CISO` (California), `ERCO` (Texas), `NYIS` (New York), `PJM`, `MISO`, `ISNE` (New England), `SWPP` (Southwest Power Pool), `BPAT` (Bonneville) |
| `type`, `type-name` | *(region)* `D` = phụ tải, `DF` = dự báo phụ tải ngày tới, `NG` = phát điện ròng, `TI` = trao đổi ròng |
| `fueltype`, `type-name` | *(fuel_type)* `SUN`, `WND`, `NG`, `COL`, `NUC`, `WAT`, `OIL`, `OTH`, … |
| `value`, `value-units` | MWh |

### 5.4. `energy/entsoe/<dataset>` (dạng dài)

| Cột | Ý nghĩa |
|---|---|
| `timestamp` | UTC (có nước dùng bước 15 phút) |
| `country` | `DE_LU`, `FR`, `ES`, `NL`, `BE`, `PL`, `AT` |
| `dataset` | `load`, `load_forecast`, `generation`, `wind_solar_forecast`, `day_ahead_price` |
| `variable` | Ví dụ `Actual Load`, `Solar | Actual Aggregated`, `Hydro Pumped Storage | Actual Consumption`, `Wind Onshore` |
| `value` | MW (phụ tải/sản lượng) hoặc €/MWh (giá; riêng PL có thể là PLN) |

Anh (GB) không có trong danh sách vì đã ngừng công bố dữ liệu lên ENTSO-E sau Brexit.

### 5.5. `realestate/batdongsan/listings`

| Cột | Ý nghĩa |
|---|---|
| `listing_id` | Mã tin (lấy từ thuộc tính `prid` hoặc đuôi `-prXXXXXXXX` của URL) |
| `scraped_date`, `scraped_at` | Ngày/giờ thu thập (khoá: `listing_id` + `scraped_date`) |
| `category` | `apartment_sale`, `house_sale`, `land_sale` |
| `city` | `hcm`, `hanoi`, `danang` |
| `title`, `location`, `url` | Tiêu đề, khu vực hiển thị, link |
| `price_text`, `price_vnd` | Giá gốc dạng chữ và giá quy đổi ra VNĐ (`3,5 tỷ` → 3.5e9; `25 triệu/m²` × diện tích; `Thỏa thuận` → rỗng) |
| `area_m2`, `price_per_m2_text` | Diện tích, đơn giá dạng chữ |
| `bedrooms`, `toilets` | Số phòng ngủ, số WC |
| `published_text` | Thời gian đăng hiển thị trên thẻ tin |
| `is_vip` | Tin VIP (được đẩy lên đầu, xem mục 11) |

### 5.6. `realestate/batdongsan/details`
`listing_id`, `fetched_at`, `latitude`, `longitude` (lấy từ bản đồ nhúng), `address`, `description` (toàn văn mô tả, dùng cho NLP), `posted_date`, `expiry_date`, `listing_type`, `specs_json` (bảng thông số dạng JSON: pháp lý, hướng nhà, nội thất, …).

Mật độ tiện ích xung quanh **không** được cào. Nên tính sau từ `latitude`/`longitude` với OpenStreetMap (Overpass API hoặc file `.osm.pbf` của Việt Nam), vì cách này tái lập được và không phụ thuộc vào trang bất động sản.

### 5.7. `realestate/zillow/<dataset>`
Dạng rộng của Zillow: `RegionID`, `SizeRank`, `RegionName`, `RegionType`, `StateName`, …, sau đó mỗi tháng một cột (`2000-01-31`, …). Mỗi file là một bản phát hành trọn vẹn; tên file là tháng mới nhất trong bản đó.
- `zhvi_*`: Zillow Home Value Index (nhà ở riêng + căn hộ, phân khúc giữa, đã làm mượt và điều chỉnh mùa vụ).
- `zori_metro`: Zillow Observed Rent Index.

### 5.8. `patents/uspto/grants`

| Cột | Ý nghĩa |
|---|---|
| `patent_id`, `patent_date`, `filing_date`, `patent_type` | Số bằng, ngày cấp, ngày nộp đơn, loại |
| `title`, `abstract`, `num_claims` | |
| `cpc_subclasses`, `cpc_groups` | Danh sách CPC hiện hành, phân tách bằng `;` (ví dụ `G06N;G05B`, `G06N3/08;G05B13/02`) |
| `ipc` | IPC subclass, phân tách bằng `;` |
| `assignees`, `assignee_countries`, `inventor_countries` | Phân tách bằng `;` |

### 5.9. `patents/lens/publications`

| Cột | Ý nghĩa |
|---|---|
| `lens_id` | Khoá chính |
| `jurisdiction`, `doc_number`, `kind` | Ví dụ `WO 2026123456 A1` |
| `date_published`, `filing_date` | |
| `title`, `abstract` | Ưu tiên tiếng Anh |
| `num_claims`, `first_claim` | Số yêu cầu bảo hộ và claim 1 (thường là claim độc lập) |
| `claims` | Toàn bộ claims, chỉ có khi đặt `LENS_FULL_CLAIMS=1` |
| `cpc`, `ipcr` | Mã phân loại, phân tách bằng `;` |
| `applicants`, `applicant_countries`, `family_size` | |

---

## 6. Chạy thủ công & backfill dữ liệu lịch sử

Mỗi workflow có nút **Run workflow** kèm tham số:

| Workflow | Tham số | Mặc định | Ví dụ backfill |
|---|---|---|---|
| Energy | `lookback_days` | 3 (weather), 7 (EIA), 3 (ENTSO-E) | `365` → EIA và ENTSO-E lấy lại 1 năm (weather tối đa 92 ngày) |
| Real-estate | `max_pages`, `detail_limit` | 5, 80 | `20`, `300` |
| Patents | `uspto_lookback_days`, `lens_lookback_days` | 180, 14 | `1825` (5 năm), `365` |

Lời khuyên khi backfill:
- Dữ liệu 3–6 tháng thường **không đủ** cho bài báo Q1 về dự báo, vì cần nhiều mùa và nhiều năm. Nên backfill lịch sử ngay từ đầu: EIA-930 có từ 07/2015, ENTSO-E từ 2015, PatentsView từ 1976.
- Nên backfill **từng khúc** (ví dụ mỗi lần 180–365 ngày) để không vượt `timeout-minutes` của job (60 phút với energy, 120 phút với patents).
- Upsert bảo đảm không bị trùng khi các khúc chồng lên nhau.

---

## 7. Chạy trên máy cá nhân

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

export EIA_API_KEY=...            # Windows PowerShell: $env:EIA_API_KEY="..."
python -m scrapers.energy.weather_collector
python -m scrapers.energy.eia_collector
python -m scrapers.realestate.batdongsan_collector
python scripts/build_catalog.py energy

python -m pytest -q               # test offline, không gọi mạng
```

Luôn chạy từ **thư mục gốc repo** bằng `python -m ...`.

Biến môi trường hỗ trợ:

| Biến | Mặc định | Tác dụng |
|---|---|---|
| `WEATHER_PAST_DAYS` / `WEATHER_FORECAST_DAYS` | 3 / 2 | Cửa sổ Open-Meteo (quá khứ tối đa 92) |
| `EIA_LOOKBACK_DAYS` | 7 | |
| `ENTSOE_LOOKBACK_DAYS` | 3 | |
| `BDS_MAX_PAGES` / `BDS_DETAIL_LIMIT` | 5 / 80 | |
| `PATENTSVIEW_LOOKBACK_DAYS` | 180 | |
| `LENS_LOOKBACK_DAYS` / `LENS_MAX_RECORDS` | 14 / 20000 | |
| `LENS_JURISDICTIONS` | `WO,EP,US` | Ví dụ `WO,EP,US,CN,JP,KR` (khối lượng tăng rất nhanh) |
| `LENS_FULL_CLAIMS` | *(tắt)* | `1` = lưu toàn bộ claims (file lớn hơn khoảng 10 lần) |

---

## 8. Đọc dữ liệu để phân tích

```python
from pathlib import Path
import pandas as pd

def load(table, pattern="*.csv*"):
    files = sorted(Path("data", table).glob(pattern))
    return pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

# Phụ tải Texas theo giờ, dạng bảng rộng: cột = type (D, DF, NG, TI)
eia = load("energy/eia/region")
ercot = (eia[eia.respondent == "ERCO"]
         .assign(period=lambda d: pd.to_datetime(d.period, utc=True))
         .pivot_table(index="period", columns="type", values="value"))

# Ghép thời tiết Houston vào phụ tải ERCOT
wx = load("energy/weather/observed")
wx = wx[wx.location == "US_ERCO_Houston"].assign(time=lambda d: pd.to_datetime(d.time, utc=True)).set_index("time")
df = ercot.join(wx[["temperature_2m", "shortwave_radiation"]], how="inner")

# Dự báo thời tiết được phát hành trước thời điểm t tối thiểu 24h (tránh rò rỉ thông tin tương lai)
fc = load("energy/weather/forecast")
fc[["time", "issued_at"]] = fc[["time", "issued_at"]].apply(pd.to_datetime, utc=True)
fc = fc[(fc.time - fc.issued_at) >= pd.Timedelta("24h")].sort_values("issued_at").groupby(["location", "time"]).last()

# Ghép toạ độ và mô tả vào ảnh chụp giá hằng ngày của Batdongsan
panel = load("realestate/batdongsan/listings").merge(
    load("realestate/batdongsan/details"), on="listing_id", how="left")

# Mạng đồng xuất hiện CPC subclass (cho phân tích hội tụ công nghệ)
pat = load("patents/uspto/grants", "*.csv.gz")
pairs = (pat.cpc_subclasses.dropna().str.split(";")
         .apply(lambda s: [(a, b) for i, a in enumerate(sorted(set(s))) for b in sorted(set(s))[i + 1:]])
         .explode().dropna().value_counts())
```

Repo sẽ lớn dần, nên khi chỉ cần dữ liệu mới nhất có thể clone nông: `git clone --depth 1 ...`.

---

## 9. Giám sát & bảo trì

| Việc | Cách làm |
|---|---|
| Biết khi có lỗi | Khi job *failed*, GitHub gửi email cho người sửa cron gần nhất. Bật trong *Settings (tài khoản) → Notifications → Actions* |
| Kiểm tra dữ liệu có vào đều | Xem cột **To** trong `data/*/CATALOG.md`: energy phải trong vòng khoảng 1 ngày, bất động sản khoảng 1 ngày, Lens khoảng 1 tuần; PatentsView có thể trễ tới 1 quý (xem mục 11) |
| Workflow bị tắt | `keepalive.yml` bật lại hằng tuần. Nếu vẫn thấy biểu tượng *disabled* trong tab Actions thì bấm *Enable workflow* |
| Lỗi `HTTP 4xx ... <thông báo>` | Đọc thông báo API in ra trong log. Thường do sai hoặc hết hạn key, hoặc API đổi tên trường |
| Batdongsan `0 listings parsed - markup probably changed` | Trang đã đổi HTML. Mở trang bằng trình duyệt, xem mã nguồn, cập nhật các selector trong `parse_cards` / `parse_detail` của `scrapers/realestate/batdongsan_collector.py`, cập nhật HTML mẫu trong `tests/test_realestate.py` |
| Batdongsan `blocked by anti-bot protection` | Xem mục 11 |
| Lens `stored X of Y matches` | Tăng `LENS_MAX_RECORDS` hoặc thu hẹp `LENS_JURISDICTIONS` / danh sách CPC |
| Cập nhật thư viện | Sửa phiên bản trong `requirements.txt` (đang pin cố định để lịch chạy dài hạn không bị vỡ đột ngột), chạy `pytest`, rồi push |

---

## 10. Tuỳ biến

| Muốn thay đổi | Sửa ở đâu |
|---|---|
| Thêm hoặc bớt điểm thời tiết | `LOCATIONS` trong `scrapers/energy/weather_collector.py` |
| Biến thời tiết / chất lượng không khí | `WEATHER_VARS`, `AQ_VARS` (tên biến theo tài liệu Open-Meteo) |
| Vùng lưới Mỹ | `RESPONDENTS` trong `eia_collector.py` |
| Nước / vùng giá châu Âu | `ZONES` trong `entsoe_collector.py` (mã theo `entsoe.mappings.Area`) |
| Loại BĐS, thành phố | `SEARCHES` trong `batdongsan_collector.py`: đường dẫn trang tìm kiếm, ví dụ `ban-can-ho-chung-cu-binh-duong` |
| Lĩnh vực công nghệ | `CPC_SUBCLASSES` trong `scrapers/patents/common.py` (dùng chung cho USPTO và Lens) |
| Tần suất chạy | Dòng `cron:` trong `.github/workflows/*.yml` |

Danh sách CPC hiện tại: G06N (AI), G16H (tin học y tế), A61B (chẩn đoán/thiết bị y tế), H04W (mạng không dây), G16Y (IoT), G05B (điều khiển), H02J (lưới điện/lưu trữ), Y02E (năng lượng giảm phát thải), F03D (tua-bin gió), H01M (pin), H10K (điện tử hữu cơ/OLED/OPV), G02B (quang học/thấu kính), H01S (laser). G06F và H04L cố tình bị loại vì quá rộng: chúng sẽ chiếm phần lớn dung lượng mà làm nhiễu phân tích hội tụ.

---

## 11. Giới hạn & rủi ro đã biết

**Kỹ thuật**
- **Batdongsan có thể chặn IP của GitHub Actions.** Các trang có lớp chống bot (Cloudflare/captcha) thường chặn dải IP máy chủ đám mây. Khi bị chặn, job lưu phần đã lấy được rồi báo *failed*. Nếu tình trạng lặp lại, phải chạy collector này trên máy/VPS tại Việt Nam (cron của hệ điều hành hoặc [self-hosted runner](https://docs.github.com/actions/hosting-your-own-runners) với `runs-on: self-hosted`).
- **Selector HTML của Batdongsan** viết theo cấu trúc trang tại thời điểm phát triển và sẽ hỏng khi trang đổi giao diện; job sẽ báo lỗi rõ để sửa (mục 9).
- **PatentsView cập nhật cơ sở dữ liệu khoảng mỗi quý**, nên phần lớn các lần chạy hằng tuần sẽ không có bằng mới. Đây là đặc tính của nguồn, không phải lỗi. Lens cập nhật thường xuyên hơn.
- **Dung lượng repo** tăng theo thời gian (ước tính khoảng vài chục MB/tháng CSV chưa nén cho nhóm năng lượng; git nén lại được nhiều). Khi repo vượt khoảng 1 GB, nên chuyển dữ liệu cũ sang GitHub Releases, Hugging Face Datasets hoặc Zenodo (Zenodo có DOI để trích dẫn trong bài báo).
- Việc bật lại workflow qua API trong `keepalive.yml` có thực sự reset bộ đếm 60 ngày hay không thì GitHub không công bố rõ; các commit dữ liệu thường xuyên của bot cũng giữ repo hoạt động.

**Phạm vi & tính hợp lệ của dữ liệu cho nghiên cứu**
- **Batdongsan là giá chào bán, không phải giá giao dịch.** Trang kết quả còn ưu tiên tin VIP và tin mới, nên mẫu thu được **không ngẫu nhiên** (có selection bias). Cần nêu rõ điều này và kiểm định độ nhạy (ví dụ loại tin VIP) khi dùng cho mô hình hedonic.
- Ảnh chụp giá hằng ngày chỉ ghi được những tin còn nằm trong vài trang đầu. Một tin có thể biến mất khỏi dữ liệu vì bị đẩy xuống trang sau, không nhất thiết vì đã bán.
- **Zillow Research là chỉ số tổng hợp theo vùng**, không có dữ liệu từng căn. Không cào listing Zillow vì Điều khoản sử dụng của Zillow cấm việc này.
- **Không cào Google Patents** (không có API công khai, chặn truy vấn tự động). PatentsView + Lens thay thế với dữ liệu có cấu trúc tốt hơn.
- **Lens mặc định chỉ lấy WO/EP/US.** Muốn phủ Trung Quốc, Nhật, Hàn thì thêm `CN,JP,KR`, khối lượng sẽ tăng nhiều lần.
- Open-Meteo `observed` là dữ liệu mô hình, không phải số đo trạm.

**Tuân thủ điều khoản**
- Collector Batdongsan giãn cách 3–6 giây/request và chỉ đọc trang công khai. Người dùng tự chịu trách nhiệm tuân thủ Điều khoản sử dụng của trang và quy định về dữ liệu cá nhân: dữ liệu thô có thể chứa tên hoặc số điện thoại người đăng trong phần mô tả, nên cần ẩn danh trước khi công bố.
- Dữ liệu từ EIA (public domain), ENTSO-E, Open-Meteo (CC BY 4.0), Lens và Zillow Research có điều kiện trích dẫn và giấy phép riêng. Cần ghi nguồn đúng khi công bố bài báo hoặc bộ dữ liệu.

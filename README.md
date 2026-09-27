# Collectdata — Thu thập dữ liệu nghiên cứu tự động

Hệ thống thu thập dữ liệu **hiện tại và lịch sử** bằng **GitHub Actions** (không cần máy chủ riêng), chỉ dùng nguồn **miễn phí**:

| Nhóm | Mục đích nghiên cứu | Nguồn | Cần key? | Lịch sử có thể lấy |
|---|---|---|---|---|
| **Năng lượng & môi trường** | Dự báo phụ tải ngắn hạn (STLF), dự báo gió/mặt trời, mô hình không–thời gian | EIA-930 (lưới điện Mỹ) | `EIA_API_KEY` (miễn phí) | từ 07/2015 |
| | | Open-Meteo: ERA5, dự báo, chất lượng không khí | không | ERA5 từ 1940; chất lượng không khí từ 08/2022 |
| **Bất động sản** | Định giá hedonic, phân tích không gian, tác động hạ tầng | Zillow Research | không | từ 2000 (có sẵn trong mỗi bản phát hành) |
| | | batdongsan.com.vn | không | **chỉ từ lúc bắt đầu cào** |

Mỗi lần chạy, dữ liệu được **gộp (upsert)** vào các file CSV theo tháng trong `data/`, rồi bot tự commit và push lại vào repo. Dữ liệu lịch sử được **backfill tự động theo từng phần** qua nhiều lượt chạy cho đến khi xong.

---

## Mục lục

1. [Kiến trúc](#1-kiến-trúc)
2. [Lịch chạy](#2-lịch-chạy)
3. [Cài đặt lần đầu](#3-cài-đặt-lần-đầu)
4. [Lấy dữ liệu lịch sử (backfill)](#4-lấy-dữ-liệu-lịch-sử-backfill)
5. [Cấu trúc dữ liệu](#5-cấu-trúc-dữ-liệu)
6. [Từ điển dữ liệu](#6-từ-điển-dữ-liệu-data-dictionary)
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
  ├── keepalive.yml           ── hằng tuần ──▶ bật lại các workflow (tránh bị GitHub tự tắt)
  └── ci.yml                  ── mỗi push   ──▶ pytest (không chạy khi chỉ data/ thay đổi)

Mỗi lượt chạy một collector:
  1. Thu thập cửa sổ gần đây (vài ngày)            ─┐
  2. Nếu có kế hoạch backfill còn dang dở:          ├─▶ utils/storage.upsert() ─▶ data/<nhóm>/<nguồn>/<bảng>/YYYY-MM.csv[.gz]
     tải tiếp từng phần lịch sử đến khi hết giờ     ─┘
  3. scripts/commit_data.sh: nén tháng cũ ─▶ cập nhật CATALOG.md ─▶ commit ─▶ pull --rebase ─▶ push
  4. scripts/continue_backfill.sh: nếu backfill chưa xong ─▶ tự kích hoạt lượt chạy tiếp theo
```

```
.
├── .github/workflows/        # lịch chạy, keepalive, CI
├── scrapers/
│   ├── energy/               # weather_collector (Open-Meteo), eia_collector
│   └── realestate/           # batdongsan_collector, zillow_collector
├── utils/
│   ├── http.py               # session có retry/backoff, check() lỗi API, đọc biến môi trường
│   ├── storage.py            # upsert theo tháng, nén tháng cũ, chỉ ghi khi nội dung đổi
│   └── backfill.py           # kế hoạch backfill có thể tiếp tục, chia phần, quỹ thời gian
├── scripts/
│   ├── commit_data.sh        # commit + push an toàn khi nhiều workflow chạy đồng thời
│   ├── continue_backfill.sh  # tự kích hoạt lượt chạy tiếp khi backfill chưa xong
│   └── build_catalog.py      # sinh data/<nhóm>/CATALOG.md
├── tests/                    # pytest, mock HTTP — không gọi mạng
└── data/                     # dữ liệu (bot tự cập nhật)
```

### Các nguyên tắc thiết kế

- **Upsert với cửa sổ chồng lấn:** mỗi lần chạy lấy lại vài ngày gần nhất. Nhờ vậy, nếu một lần cron bị trễ hoặc lỗi thì lần sau tự lấp khoảng trống, và các giá trị được nguồn sửa lại sau (EIA-930 thường sửa số liệu trong vài ngày) sẽ ghi đè bản cũ theo khoá chính.
- **Phân vùng theo tháng.** Tháng gần đây (≤ 2 tháng) để dạng `.csv` thường, vì git nén rất tốt các thay đổi nhỏ. Tháng cũ tự được nén thành `.csv.gz` với nội dung byte cố định, nên git không bao giờ lưu thêm bản sao nếu dữ liệu không đổi.
- **Backfill có thể tiếp tục:** lịch sử được chia thành từng phần (tháng, hoặc năm × địa điểm). Tiến độ lưu trong `data/<nhóm>/_backfill.json`. Một lượt chạy chỉ dùng tối đa một quỹ thời gian cho backfill; phần còn lại do lượt sau, tự kích hoạt hoặc theo lịch, làm tiếp.
- **Mỗi workflow chỉ ghi vào thư mục nhóm của mình** và luôn checkout đầu nhánh mới nhất, nên khi hai workflow push gần nhau, `pull --rebase` không bao giờ xung đột.
- **Một nguồn lỗi không làm mất nguồn khác:** dữ liệu được commit ngay sau mỗi nguồn; một lỗi tạm thời chỉ dừng backfill của nguồn đó đến lượt sau.
- **Thiếu API key thì bỏ qua (exit 0) kèm cảnh báo**, nhưng kế hoạch backfill vẫn được ghi nhận, nên khi thêm key thì lượt chạy kế tiếp tự lấy lịch sử.
- **Mọi thời gian lưu theo UTC**, định dạng `YYYY-MM-DDTHH:MMZ`.

---

## 2. Lịch chạy

| Workflow | Cron (UTC) | Giờ Việt Nam | Cửa sổ gần đây mỗi lần chạy | Quỹ thời gian backfill / lượt |
|---|---|---|---|---|
| `collect_energy.yml` | `23 */6 * * *` | 06:23, 12:23, 18:23, 00:23 | Open-Meteo: 3 ngày quá khứ + 2 ngày dự báo + 14 ngày ERA5; EIA: 7 ngày | 95 phút cho mỗi bước (thời tiết, EIA) |
| `collect_realestate.yml` | `37 1 * * *` | 08:37 hằng ngày | 5 trang × 6 danh mục Batdongsan; tối đa 80 trang chi tiết mới | — |
| `keepalive.yml` | `0 6 * * 1` | 13:00 thứ Hai | — | — |

**Vì sao năng lượng chạy 6 giờ/lần mà không phải mỗi giờ?** Dữ liệu vẫn có độ phân giải giờ; chỉ tần suất *gọi API* là 6 giờ. Vì mỗi lần lấy lại cả cửa sổ nhiều ngày nên không mất giờ nào. Riêng bảng dự báo thời tiết thì chạy dày hơn sẽ có nhiều "phiên bản dự báo" hơn; có thể đổi dòng `cron`.

> GitHub **không đảm bảo** cron chạy đúng phút; lúc tải cao có thể trễ hoặc bỏ lượt. Cửa sổ chồng lấn ở trên sinh ra để bù cho điều này.

---

## 3. Cài đặt lần đầu

### 3.1. Nhánh mặc định

Cron **chỉ chạy trên nhánh mặc định** của repo. Hiện nhánh mặc định là `claude/upbeat-cori-snhhva`. Có thể tạo `main` từ nhánh này rồi đặt làm mặc định (*Settings → General → Default branch*); mọi thứ vẫn hoạt động vì workflow tự dùng nhánh đang chạy.

### 3.2. Quyền của Actions

*Settings → Actions → General*:
- **Actions permissions:** Allow all actions.
- **Workflow permissions:** các workflow đã tự khai báo `contents: write` (để commit dữ liệu) và `actions: write` (để tự kích hoạt lượt backfill tiếp theo). Nếu tổ chức giới hạn token ở mức read-only thì cần chọn **Read and write permissions**.

### 3.3. EIA API key

1. Đăng ký miễn phí tại <https://www.eia.gov/opendata/register.php>; key được gửi qua email.
2. *Settings → Secrets and variables → Actions → New repository secret*.
3. **Name:** `EIA_API_KEY`, **Secret:** dán key, rồi bấm *Add secret*.

> **Tuyệt đối không dán key vào code, README hay file trong repo:** repo đang **public**, ai cũng đọc được. GitHub Secrets được mã hoá và tự bị che (`***`) trong log.

### 3.4. Chạy thử

*Actions → chọn workflow → Run workflow* (để trống các ô). Sau đó kiểm tra log và file `data/<nhóm>/CATALOG.md`.

### 3.5. Batdongsan: chạy trên máy của bạn (self-hosted runner)

batdongsan.com.vn **chặn IP máy chủ của GitHub** (đã xác nhận: HTTP 403 từ trang chống bot). Collector này cần chạy từ một máy có IP thông thường ở Việt Nam (máy tính cá nhân, mini PC, VPS trong nước):

1. *Settings → Actions → Runners → New self-hosted runner*, chọn hệ điều hành và làm theo lệnh hiển thị (tải, `./config.sh`, `./run.sh` hoặc cài dạng service để chạy nền). Nên dùng Linux/macOS; trên Windows cần có Git Bash.
2. Máy cần có Python 3.12 (hoặc để `actions/setup-python` tự cài) và phải bật đúng giờ cron (08:37 sáng).
3. *Settings → Secrets and variables → Actions → Variables → New repository variable*: tên `BDS_RUNNER`, giá trị `self-hosted` (hoặc nhãn riêng bạn đặt cho runner).

Khi chưa đặt `BDS_RUNNER`, job Batdongsan vẫn thử trên máy GitHub. Nếu bị chặn, job báo lỗi nhưng không làm workflow thất bại, và phần Zillow vẫn được lưu bình thường.

---

## 4. Lấy dữ liệu lịch sử (backfill)

### 4.1. Bắt đầu

*Actions → Collect energy data* → **Run workflow** → điền:

| Ô | Giá trị | Ý nghĩa |
|---|---|---|
| `backfill_start` | `auto` | Mỗi nguồn lấy từ mốc mặc định (bảng dưới) |
| | `2010-01-01` | Lấy từ ngày cụ thể (không sớm hơn mốc sớm nhất của nguồn) |
| `backfill_end` | *(trống)* | Đến hôm nay |
| `backfill_sources` | *(trống)* hoặc `era5,eia` | Chỉ backfill một số nguồn |

| Nguồn (`backfill_sources`) | Mốc `auto` | Mốc sớm nhất có thể | Đơn vị chia phần | Ước tính dung lượng khi xong* |
|---|---|---|---|---|
| `era5` (thời tiết tái phân tích) | 2015-01-01 | 1940-01-01 | năm × địa điểm | ~55 MB |
| `airquality` | 2022-08-01 | 2022-08-01 | năm × địa điểm | ~12 MB |
| `eia` | 2015-07-01 | 2015-07-01 | tháng | ~90 MB |

\* Dung lượng nén trong repo, **[ước tính]** từ kích thước thực đo của dữ liệu Open-Meteo (~94 byte/dòng, gzip ~4 lần) và số dòng dự kiến. Con số thật sẽ hiện trong `CATALOG.md`.

ERA5 mặc định từ 2015 để khớp với dữ liệu phụ tải EIA; thời tiết trước đó không có phụ tải để ghép. Muốn lấy xa hơn thì điền ngày cụ thể, ví dụ `1990-01-01` với `backfill_sources` = `era5` (khoảng 55 MB cho mỗi 11 năm [ước tính]).

> Backfill `auto` đã được kích hoạt ngày 27/09/2026. Kế hoạch EIA đã được ghi nhận sẵn, nên chỉ cần thêm `EIA_API_KEY` (mục 3.3); lượt chạy kế tiếp sẽ tự lấy lịch sử EIA.

### 4.2. Cách backfill chạy

- Lượt chạy đầu ghi kế hoạch vào `data/energy/_backfill.json`, tải phần gần nhất trong quỹ thời gian, commit, rồi **tự kích hoạt lượt tiếp theo** (tối đa 40 lượt nối tiếp). Sau đó các lượt chạy theo lịch tiếp tục đến khi xong.
- Theo dõi tiến độ ở mục **Backfill progress** trong `data/energy/CATALOG.md` (số phần đã xong / tổng, số phần bị bỏ qua do nguồn không có dữ liệu, số phần còn lại).
- Phần nào bị nguồn trả lỗi cố định (HTTP 400/404/422) được đánh dấu **skipped** để không lặp vô hạn. Lỗi tạm thời (429, 5xx, mất kết nối) thì dừng và thử lại ở lượt sau.
- Chạy lại backfill với khoảng rộng hơn sẽ **mở rộng** kế hoạch; các phần đã xong không bị tải lại.

### 4.3. Thời gian dự kiến [ước tính]

| Nguồn | Số phần | Thời gian | Yếu tố giới hạn |
|---|---|---|---|
| `era5` (2015→) + `airquality` | ~260 + ~110 | 1–2 ngày | Hạn mức Open-Meteo miễn phí (~10.000 lượt/ngày; một request dài nhiều biến được tính thành nhiều lượt). Code nghỉ 30 giây giữa các request (`OPEN_METEO_PAUSE_SECONDS`) |
| `eia` | ~135 tháng | 1–2 giờ sau khi có key | |

---

## 5. Cấu trúc dữ liệu

```
data/
├── energy/
│   ├── CATALOG.md                        # tự sinh: bảng, số dòng, khoảng thời gian, tiến độ backfill
│   ├── _backfill.json                    # kế hoạch & tiến độ backfill
│   ├── _catalog_cache.json               # bộ đệm thống kê (không cần quan tâm)
│   ├── weather/
│   │   ├── era5/YYYY-MM.csv[.gz]         # ERA5 theo giờ, lịch sử liên tục đến ~6 ngày trước
│   │   ├── observed/YYYY-MM.csv[.gz]     # giá trị phân tích của mô hình dự báo, vài ngày gần nhất
│   │   └── forecast/YYYY-MM.csv[.gz]     # MỌI bản dự báo, theo thời điểm phát hành (issued_at)
│   ├── airquality/observed/…             # PM2.5, PM10, NO2, O3, SO2, CO, US AQI
│   └── eia/
│       ├── region/…                      # phụ tải, dự báo phụ tải, phát điện ròng, trao đổi
│       └── fuel_type/…                   # phát điện theo nhiên liệu
└── realestate/
    ├── CATALOG.md
    ├── batdongsan/
    │   ├── listings/…                    # ảnh chụp hằng ngày: 1 dòng / (tin đăng, ngày)
    │   └── details/…                     # 1 dòng / tin đăng: toạ độ, mô tả, thông số
    └── zillow/
        ├── zhvi_metro/YYYY-MM.csv.gz     # chỉ giữ bản phát hành mới nhất (chứa toàn bộ lịch sử)
        ├── zhvi_county/YYYY-MM.csv.gz
        └── zori_metro/YYYY-MM.csv.gz
```

Quy ước:
- **Tên file = tháng của cột thời gian** trong bảng, không phải tháng thu thập. Riêng `forecast` phân vùng theo `issued_at`, `listings` theo `scraped_at`.
- **`.csv` và `.csv.gz` cùng tồn tại** trong một bảng: tháng gần đây để dạng thường, tháng cũ được nén. `pandas.read_csv` đọc cả hai.
- **Giá trị rỗng** được lưu thành chuỗi rỗng.

---

## 6. Từ điển dữ liệu (data dictionary)

> Tên cột của Open-Meteo và Zillow đã được xác nhận qua lần chạy thật. Tên cột của EIA viết theo tài liệu API và cần đối chiếu lại sau lần chạy đầu có key.

### 6.1. `energy/weather/era5`, `observed`, `forecast`

| Cột | Ý nghĩa |
|---|---|
| `location` | Mã điểm `<quốc gia>_<vùng lưới>_<thành phố>`, ví dụ `US_ERCO_Houston`, `DE_Berlin`, `VN_HoChiMinh` (22 điểm, xem `LOCATIONS` trong `weather_collector.py`) |
| `issued_at` | *(chỉ ở forecast)* thời điểm lấy bản dự báo (UTC, làm tròn xuống giờ) |
| `time` | Giờ hiệu lực (UTC) |
| `temperature_2m`, `apparent_temperature`, `dew_point_2m` | °C |
| `relative_humidity_2m` | % |
| `precipitation` | mm |
| `cloud_cover` | % |
| `surface_pressure` | hPa |
| `wind_speed_10m`, `wind_speed_100m`, `wind_gusts_10m` | km/h (100 m sát chiều cao hub turbine) |
| `wind_direction_100m` | độ |
| `shortwave_radiation`, `direct_normal_irradiance`, `diffuse_radiation` | W/m² (GHI, DNI, DHI) |

Ba bảng dùng cho ba mục đích khác nhau:
- **`era5`**: bộ dữ liệu tái phân tích ERA5, chuẩn cho bài báo, trễ khoảng 5–6 ngày. Dùng làm **thời tiết thực tế** cho huấn luyện và phân tích.
- **`observed`**: giá trị phân tích của mô hình dự báo trong vài ngày gần nhất, dùng khi cần số liệu mới hơn ERA5.
- **`forecast`**: **mọi phiên bản dự báo** kể từ ngày bắt đầu cào; phần này **không backfill được**. Dùng để đánh giá STLF bằng đúng thông tin thời tiết có sẵn tại thời điểm dự báo, thay vì dùng thời tiết thực tế làm đầu vào (cách đó làm kết quả lạc quan hơn thực tế).

Các điểm ở Đức, Pháp, Tây Ban Nha, Hà Lan, Bỉ, Ba Lan, Áo được giữ lại để có dữ liệu thời tiết châu Âu, dù phụ tải châu Âu (ENTSO-E) không còn trong dự án.

### 6.2. `energy/airquality/observed`
`location`, `time`, `pm10`, `pm2_5` (µg/m³), `nitrogen_dioxide`, `ozone`, `sulphur_dioxide`, `carbon_monoxide` (µg/m³), `us_aqi`.

### 6.3. `energy/eia/region` & `energy/eia/fuel_type`

| Cột | Ý nghĩa |
|---|---|
| `period` | Giờ (UTC) |
| `respondent` | Vùng cân bằng: `CISO` California ISO · `ERCO` ERCOT (Texas) · `NYIS` New York ISO · `PJM` PJM Interconnection · `MISO` Midcontinent ISO · `ISNE` ISO New England · `SWPP` Southwest Power Pool · `BPAT` Bonneville Power Administration |
| `type` | *(region)* `D` = phụ tải, `DF` = dự báo phụ tải ngày tới, `NG` = phát điện ròng, `TI` = trao đổi ròng |
| `fueltype` | *(fuel_type)* `SUN` mặt trời, `WND` gió, `NG` khí, `COL` than, `NUC` hạt nhân, `WAT` thủy điện, `OIL` dầu, `OTH` khác, … |
| `value` | MWh |

Các cột mô tả (`respondent-name`, `type-name`, `value-units`) bị bỏ để giảm khoảng 60% dung lượng lịch sử; ý nghĩa của chúng nằm trong bảng trên.

### 6.4. `realestate/batdongsan/listings`

| Cột | Ý nghĩa |
|---|---|
| `listing_id` | Mã tin (thuộc tính `prid` hoặc đuôi `-prXXXXXXXX` của URL) |
| `scraped_date`, `scraped_at` | Ngày/giờ thu thập (khoá: `listing_id` + `scraped_date`) |
| `category` | `apartment_sale`, `house_sale`, `land_sale` |
| `city` | `hcm`, `hanoi`, `danang` |
| `title`, `location`, `url` | Tiêu đề (đã che số điện thoại), khu vực hiển thị, link |
| `price_text`, `price_vnd` | Giá gốc dạng chữ và giá quy đổi ra VNĐ (`3,5 tỷ` → 3.5e9; `25 triệu/m²` × diện tích; `Thỏa thuận` → rỗng) |
| `area_m2`, `price_per_m2_text` | Diện tích, đơn giá dạng chữ |
| `bedrooms`, `toilets` | Số phòng ngủ, WC |
| `published_text` | Thời gian đăng hiển thị trên thẻ tin |
| `is_vip` | Tin VIP (được đẩy lên đầu, xem mục 11) |

### 6.5. `realestate/batdongsan/details`
`listing_id`, `fetched_at`, `latitude`, `longitude` (từ bản đồ nhúng), `address`, `description` (toàn văn mô tả cho NLP, **số điện thoại đã được thay bằng `[SĐT]`**), `posted_date`, `expiry_date`, `listing_type`, `specs_json` (bảng thông số dạng JSON: pháp lý, hướng, nội thất…).

Mật độ tiện ích xung quanh nên tính sau từ `latitude`/`longitude` với OpenStreetMap (Overpass API hoặc file `.osm.pbf` của Việt Nam), để tái lập được.

### 6.6. `realestate/zillow/<dataset>`
Dạng rộng của Zillow: `RegionID`, `SizeRank`, `RegionName`, `RegionType`, `StateName`, …, rồi mỗi tháng một cột (`2000-01-31`, …). Mỗi bản phát hành đã chứa **toàn bộ lịch sử** (ZHVI từ 01/2000, ZORI từ 2015), nên chỉ giữ bản mới nhất; các bản cũ vẫn còn trong lịch sử git.
- `zhvi_*`: Zillow Home Value Index (nhà riêng + căn hộ, phân khúc giữa, đã làm mượt và điều chỉnh mùa vụ).
- `zori_metro`: Zillow Observed Rent Index.

---

## 7. Chạy trên máy cá nhân

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

export EIA_API_KEY=...            # Windows PowerShell: $env:EIA_API_KEY="..."
python -m scrapers.energy.weather_collector
BACKFILL_START=2020-01-01 BACKFILL_SOURCES=eia BACKFILL_MINUTES=60 python -m scrapers.energy.eia_collector
python scripts/build_catalog.py energy

python -m pytest -q               # test offline, không gọi mạng
```

Luôn chạy từ **thư mục gốc repo** bằng `python -m ...`. Khi chạy trên máy cá nhân, key chỉ đặt qua biến môi trường, không ghi vào file trong repo.

| Biến môi trường | Mặc định | Tác dụng |
|---|---|---|
| `BACKFILL_START` / `BACKFILL_END` / `BACKFILL_SOURCES` | trống | Như các ô trong mục 4.1 |
| `BACKFILL_MINUTES` | 90 (workflow đặt 95) | Quỹ thời gian backfill cho một lượt chạy collector |
| `OPEN_METEO_PAUSE_SECONDS` | 30 | Thời gian nghỉ giữa các request lịch sử Open-Meteo |
| `WEATHER_PAST_DAYS` / `WEATHER_FORECAST_DAYS` | 3 / 2 | Cửa sổ gần đây của Open-Meteo (quá khứ tối đa 92) |
| `EIA_LOOKBACK_DAYS` | 7 | |
| `BDS_MAX_PAGES` / `BDS_DETAIL_LIMIT` | 5 / 80 | |

---

## 8. Đọc dữ liệu để phân tích

```python
from pathlib import Path
import pandas as pd

def load(table):
    files = sorted(Path("data", table).glob("*.csv*"))   # đọc cả .csv và .csv.gz
    return pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

# Phụ tải ERCOT theo giờ, dạng rộng: cột = D, DF, NG, TI
eia = load("energy/eia/region")
ercot = (eia[eia.respondent == "ERCO"]
         .assign(period=lambda d: pd.to_datetime(d.period, utc=True))
         .pivot_table(index="period", columns="type", values="value"))

# Sản lượng mặt trời và gió của CAISO theo giờ
fuel = load("energy/eia/fuel_type")
caiso_re = (fuel[(fuel.respondent == "CISO") & fuel.fueltype.isin(["SUN", "WND"])]
            .assign(period=lambda d: pd.to_datetime(d.period, utc=True))
            .pivot_table(index="period", columns="fueltype", values="value"))

# Ghép thời tiết ERA5 Houston vào phụ tải ERCOT
wx = load("energy/weather/era5")
wx = wx[wx.location == "US_ERCO_Houston"].assign(time=lambda d: pd.to_datetime(d.time, utc=True)).set_index("time")
df = ercot.join(wx[["temperature_2m", "shortwave_radiation"]], how="inner")

# Dự báo thời tiết phát hành trước thời điểm t tối thiểu 24h (tránh rò rỉ thông tin tương lai)
fc = load("energy/weather/forecast")
fc[["time", "issued_at"]] = fc[["time", "issued_at"]].apply(pd.to_datetime, utc=True)
fc = fc[(fc.time - fc.issued_at) >= pd.Timedelta("24h")].sort_values("issued_at").groupby(["location", "time"]).last()

# Ảnh chụp giá hằng ngày của Batdongsan + toạ độ/mô tả
panel = load("realestate/batdongsan/listings").merge(load("realestate/batdongsan/details"), on="listing_id", how="left")
```

Repo sẽ lớn dần. Khi chỉ cần một nhóm dữ liệu, có thể clone nông và thưa:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/sweetluvz/Collectdata.git
cd Collectdata && git sparse-checkout set data/energy
```

---

## 9. Giám sát & bảo trì

| Việc | Cách làm |
|---|---|
| Biết khi có lỗi | Job *failed* → GitHub gửi email cho người sửa cron gần nhất. Bật trong *Settings (tài khoản) → Notifications → Actions* |
| Kiểm tra dữ liệu có vào đều | Cột **To** trong `data/*/CATALOG.md`: energy trong vòng ~1 ngày (ERA5 ~6 ngày), bất động sản ~1 ngày |
| Tiến độ backfill | Mục **Backfill progress** trong `data/energy/CATALOG.md`. `waiting (API key missing?)` nghĩa là kế hoạch đã có nhưng chưa có key |
| Backfill dừng lâu | Xem log của bước tương ứng: `will retry next run` (lỗi tạm thời) hay `skipped`. Có thể bấm Run workflow (để trống các ô) để chạy tiếp ngay |
| Workflow bị tắt | `keepalive.yml` bật lại hằng tuần. Nếu vẫn thấy *disabled* trong tab Actions thì bấm *Enable workflow* |
| Lỗi `HTTP 4xx ... <thông báo>` | Đọc thông báo API trong log. Với EIA thường do sai hoặc hết hạn key: tạo key mới và cập nhật secret `EIA_API_KEY` |
| Batdongsan `blocked by anti-bot protection` | Xem mục 3.5 |
| Batdongsan `0 listings parsed - markup probably changed` | Trang đổi HTML. Cập nhật selector trong `parse_cards` / `parse_detail` của `batdongsan_collector.py` và HTML mẫu trong `tests/test_realestate.py` |
| Làm lại một phần backfill | Xoá mã phần đó khỏi `done`/`skipped` trong `_backfill.json`, commit, rồi chạy workflow |
| Cập nhật thư viện | Sửa phiên bản trong `requirements.txt` (đang pin cố định), chạy `pytest`, rồi push |

---

## 10. Tuỳ biến

| Muốn thay đổi | Sửa ở đâu |
|---|---|
| Điểm thời tiết | `LOCATIONS` trong `scrapers/energy/weather_collector.py`. Điểm mới cần backfill lại `era5`: chạy lại backfill, các phần của điểm mới sẽ được thêm |
| Biến thời tiết / chất lượng không khí | `WEATHER_VARS`, `AQ_VARS` (tên theo tài liệu Open-Meteo) |
| Vùng lưới Mỹ | `RESPONDENTS` trong `eia_collector.py` (danh sách mã trên <https://www.eia.gov/electricity/gridmonitor/>) |
| Loại BĐS, thành phố | `SEARCHES` trong `batdongsan_collector.py`, ví dụ `ban-can-ho-chung-cu-binh-duong` |
| Tần suất chạy | Dòng `cron:` trong `.github/workflows/*.yml` |
| Thêm nguồn có backfill | Viết collector gọi `backfill.run(...)` và thêm tên nguồn vào `SOURCES` trong `utils/backfill.py`; kế hoạch của nguồn không có trong `SOURCES` sẽ bị dọn khi build catalog |

---

## 11. Giới hạn & rủi ro đã biết

**Phạm vi đã thu hẹp (chỉ giữ nguồn miễn phí, không cần xin duyệt)**
- **Đã loại:** ENTSO-E (lưới điện châu Âu), USPTO PatentsView và Lens.org (sáng chế), vì cần xin key hoặc tài khoản được duyệt. Hướng nghiên cứu về sáng chế hiện **không có dữ liệu**. Nếu cần lại, có một nguồn không cần key là bộ tải hàng loạt (bulk download) miễn phí của PatentsView, nhưng file rất lớn (vài GB) và phải xử lý riêng.
- Nghiên cứu năng lượng chỉ còn **lưới điện Mỹ** (8 vùng EIA), không còn dữ liệu phụ tải châu Âu.

**Không thể lấy lịch sử**
- **Batdongsan**: trang chỉ hiển thị tin đang còn hạn, nên không có cách hợp lệ để lấy giá của các năm trước. Dữ liệu chỉ bắt đầu từ ngày collector chạy được (mục 3.5).
- **Phiên bản dự báo thời tiết** (`forecast`): chỉ có từ ngày bắt đầu cào. "Historical Forecast API" của Open-Meteo nối các phần đầu của nhiều lượt chạy mô hình, không phải các bản dự báo phát hành tại một thời điểm, nên không thay thế được.

**Dung lượng & hạn mức**
- Backfill mặc định ước tính đưa repo lên khoảng **150–250 MB** [ước tính]. Lấy ERA5 xa hơn (đến 1940) thêm khoảng 55 MB cho mỗi 11 năm.
- Open-Meteo miễn phí: khoảng 600 lượt/phút, 5.000/giờ, 10.000/ngày, và một request dài nhiều biến được tính thành nhiều lượt [theo trang điều khoản của Open-Meteo, cách tính chính xác chưa xác minh]. Backfill ERA5 vì thế kéo dài 1–2 ngày.

**Kỹ thuật**
- Selector HTML của Batdongsan sẽ hỏng khi trang đổi giao diện; job sẽ báo lỗi rõ (mục 9).
- `keepalive.yml` bật lại workflow qua API; việc này có reset bộ đếm 60 ngày của GitHub hay không thì chưa được xác minh. Các commit dữ liệu thường xuyên của bot cũng giữ repo hoạt động.

**Tính hợp lệ của dữ liệu cho nghiên cứu**
- **Batdongsan là giá chào bán, không phải giá giao dịch.** Kết quả tìm kiếm ưu tiên tin VIP và tin mới, nên mẫu **không ngẫu nhiên** (có selection bias). Cần nêu rõ và kiểm định độ nhạy (ví dụ loại tin VIP).
- Một tin có thể biến mất khỏi ảnh chụp hằng ngày vì bị đẩy xuống trang sau, không nhất thiết vì đã bán.
- **Zillow Research là chỉ số tổng hợp theo vùng**, không có từng căn. Không cào listing Zillow vì điều khoản sử dụng cấm.
- ERA5 là dữ liệu tái phân tích trên lưới khoảng 25–30 km, không phải số đo trạm.

**Quyền riêng tư & điều khoản** (repo đang **public**)
- Số điện thoại trong tiêu đề và mô tả Batdongsan được tự động thay bằng `[SĐT]` trước khi lưu. Tên người đăng hoặc thông tin cá nhân khác trong phần mô tả tự do **không** được lọc hết; nếu công bố bộ dữ liệu thì cần rà soát thêm, hoặc chuyển repo sang private.
- Collector Batdongsan giãn cách 3–6 giây/request và chỉ đọc trang công khai. Người dùng tự chịu trách nhiệm tuân thủ điều khoản sử dụng của trang.
- EIA (public domain), Open-Meteo (CC BY 4.0), Zillow Research: cần ghi nguồn đúng khi công bố bài báo hoặc bộ dữ liệu.

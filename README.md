# Collectdata — Thu thập dữ liệu nghiên cứu tự động

Hệ thống thu thập dữ liệu **hiện tại và lịch sử** bằng **GitHub Actions** (không cần máy chủ riêng), chỉ dùng nguồn **miễn phí**. Tất cả nguồn đều không cần key, trừ EIA (key miễn phí).

| Nhóm | Nguồn | Nội dung | Lịch sử |
|---|---|---|---|
| **Lưới điện Mỹ** | EIA-930 (key miễn phí + file CSV 6 tháng không cần key) | Phụ tải, dự báo phụ tải, phát điện theo nhiên liệu của **tất cả ~80 vùng cân bằng**, dòng điện giữa các vùng, phụ tải ~90 vùng con — theo giờ | từ 07/2015 (vùng con từ 2019) |
| | EIA (key miễn phí) | Giá dầu WTI/Brent, khí Henry Hub, xăng/dầu diesel theo ngày; giá và sản lượng điện bán lẻ theo bang theo tháng | từ 1986 / 2001 |
| | NYISO | Giá điện nút (LBMP) 11 vùng New York: ngày tới và thời gian thực (cả hai theo giờ) | từ 2000 |
| **Lưới điện châu Âu** | Energy-Charts (Fraunhofer ISE) | Sản lượng theo nguồn, phụ tải, trao đổi qua biên giới của 10 nước (15 phút); giá ngày tới 13 vùng giá | từ 2015 |
| **Lưới điện Anh** | Elexon BMRS, NESO Carbon Intensity | Phát điện theo nhiên liệu, phụ tải, cường độ carbon (30 phút) | từ 2016 / 2017 |
| **Lưới điện Úc** | AEMO | Phụ tải và giá của 5 vùng NEM (5–30 phút) | từ 12/1998 |
| **Thời tiết & môi trường** | Open-Meteo | ERA5 theo giờ, các bản dự báo, chất lượng không khí tại 40 điểm (Mỹ, châu Âu, Anh, Úc, Việt Nam) | ERA5 từ 1940; không khí từ 08/2022 |
| **Bất động sản Mỹ** | Zillow Research, FHFA, Realtor.com | Chỉ số giá nhà, giá thuê, tồn kho, số giao dịch, chỉ số HPI | từ 1975–2018 tuỳ bảng |
| **Bất động sản Việt Nam** | Chợ Tốt Nhà | Tin rao bán căn hộ/nhà/đất ở TP.HCM và Hà Nội: giá, diện tích, toạ độ, pháp lý, hướng, mô tả | **chỉ từ lúc bắt đầu cào** |
| | batdongsan.com.vn | Như trên; cần máy chạy tại Việt Nam (mục 3.5) | **chỉ từ lúc bắt đầu cào** |

Mỗi lần chạy, dữ liệu được **gộp (upsert)** vào các file CSV theo tháng trong `data/`, rồi bot tự commit và push lại vào repo. Dữ liệu lịch sử được **backfill tự động theo từng phần** qua nhiều lượt chạy cho đến khi xong.

---

## Mục lục

1. [Kiến trúc](#1-kiến-trúc)
2. [Lịch chạy](#2-lịch-chạy)
3. [Cài đặt](#3-cài-đặt)
4. [Lấy dữ liệu lịch sử (backfill)](#4-lấy-dữ-liệu-lịch-sử-backfill)
5. [Cấu trúc dữ liệu](#5-cấu-trúc-dữ-liệu)
6. [Từ điển dữ liệu](#6-từ-điển-dữ-liệu-data-dictionary)
7. [Chạy trên máy cá nhân](#7-chạy-trên-máy-cá-nhân)
8. [Đọc dữ liệu để phân tích](#8-đọc-dữ-liệu-để-phân-tích) · [8.1. Xử lý sơ bộ](#81-xử-lý-sơ-bộ-processing)
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

Mỗi collector, mỗi lượt chạy:
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
│   ├── energy/               # weather, eia, europe (Energy-Charts), gb, aemo, nyiso
│   └── realestate/           # us_housing (Zillow/FHFA/Realtor), chotot, batdongsan
├── utils/
│   ├── http.py               # session có retry/backoff, check() lỗi API, đọc biến môi trường
│   ├── storage.py            # upsert theo tháng (theo dòng hoặc theo ô), nén tháng cũ, chỉ ghi khi đổi
│   ├── backfill.py           # kế hoạch backfill có thể tiếp tục, chia phần, quỹ thời gian
│   └── privacy.py            # che số điện thoại trong văn bản tin rao
├── scripts/
│   ├── commit_data.sh        # commit + push an toàn khi nhiều workflow chạy đồng thời
│   ├── continue_backfill.sh  # tự kích hoạt lượt chạy tiếp khi backfill chưa xong
│   └── build_catalog.py      # sinh data/<nhóm>/CATALOG.md
├── processing/               # xử lý sơ bộ: bảng phân tích theo giờ, sàng lọc, làm sạch Chợ Tốt (mục 8.1)
├── tests/                    # pytest, mock HTTP — không gọi mạng
├── data/                     # dữ liệu thô (bot tự cập nhật)
└── processed/                # đầu ra của processing/ (không commit, tự sinh lại bất cứ lúc nào)
```

### Các nguyên tắc thiết kế

- **Upsert với cửa sổ chồng lấn:** mỗi lần chạy lấy lại vài ngày gần nhất. Nhờ vậy, nếu một lần cron bị trễ hoặc lỗi thì lần sau tự lấp khoảng trống, và các giá trị được nguồn sửa lại sau sẽ ghi đè bản cũ theo khoá chính.
- **Bảng dạng rộng** (mỗi mốc thời gian một dòng, mỗi chuỗi số liệu một cột) cho dữ liệu lưới điện. Cách này nhỏ hơn dạng dài khoảng 10–20 lần và dùng thẳng được cho ML. Các bảng này gộp **theo từng ô**: dữ liệu mới chỉ ghi đè ô có giá trị, không xoá ô cũ.
- **Phân vùng theo tháng.** Tháng gần đây (≤ 2 tháng) để dạng `.csv` thường, vì git nén rất tốt các thay đổi nhỏ. Tháng cũ tự được nén thành `.csv.gz` với nội dung byte cố định, nên git không lưu thêm bản sao nếu dữ liệu không đổi.
- **Backfill có thể tiếp tục:** lịch sử được chia thành từng phần. Tiến độ lưu trong `data/<nhóm>/_backfill.json`. Mỗi nguồn có quỹ thời gian riêng trong một lượt chạy; phần còn lại do lượt sau làm tiếp.
- **Mỗi workflow chỉ ghi vào thư mục nhóm của mình**, checkout đầu nhánh mới nhất, và commit ngay sau mỗi nguồn. Một nguồn lỗi không làm mất dữ liệu của nguồn khác.
- **Mọi thời gian lưu theo UTC**, định dạng `YYYY-MM-DDTHH:MMZ`. Mỗi nguồn giữ quy ước gốc của nó: EIA và AEMO ghi **thời điểm kết thúc** của khoảng đo; Energy-Charts, Elexon, NYISO ghi **thời điểm bắt đầu** (xem mục 6).

---

## 2. Lịch chạy

| Workflow | Cron (UTC) | Giờ Việt Nam | Nội dung |
|---|---|---|---|
| `collect_energy.yml` | `23 */6 * * *` | 06:23, 12:23, 18:23, 00:23 | 6 bước: thời tiết → EIA → châu Âu → Anh → Úc → NYISO. Mỗi bước lấy vài ngày gần nhất rồi backfill trong quỹ 15–85 phút (EIA và châu Âu 85 phút vì còn nhiều lịch sử nhất) |
| `collect_realestate.yml` | `37 1 * * *` | 08:37 hằng ngày | Chỉ số nhà ở Mỹ, Chợ Tốt (máy GitHub); Batdongsan (máy tại Việt Nam) |
| `keepalive.yml` | `0 6 * * 1` | 13:00 thứ Hai | Bật lại các workflow |

Dữ liệu vẫn giữ độ phân giải gốc (5 phút đến 1 giờ); chỉ tần suất *gọi API* là 6 giờ. GitHub **không đảm bảo** cron chạy đúng phút, nên mỗi lượt đều lấy lại một cửa sổ chồng lấn để bù.

---

## 3. Cài đặt

### 3.1. Nhánh mặc định
Cron **chỉ chạy trên nhánh mặc định**. Hiện nhánh mặc định là `claude/upbeat-cori-snhhva`. Có thể tạo `main` từ nhánh này rồi đặt làm mặc định (*Settings → General → Default branch*).

### 3.2. Quyền của Actions
*Settings → Actions → General*: **Allow all actions**. Các workflow đã tự khai báo `contents: write` và `actions: write`. Nếu tổ chức giới hạn token ở mức read-only thì cần chọn **Read and write permissions**.

### 3.3. EIA API key (nguồn duy nhất cần key)
1. Đăng ký miễn phí tại <https://www.eia.gov/opendata/register.php>.
2. *Settings → Secrets and variables → Actions → New repository secret*: **Name** `EIA_API_KEY`, **Secret** là key của bạn.

> **Không dán key vào bất kỳ file nào trong repo:** repo đang **public**. GitHub Secrets được mã hoá và tự bị che (`***`) trong log.

### 3.4. Chạy thử
*Actions → chọn workflow → Run workflow* (để trống các ô), rồi xem log và `data/<nhóm>/CATALOG.md`.

### 3.5. Batdongsan (tuỳ chọn): chạy trên máy tại Việt Nam
batdongsan.com.vn **chặn IP máy chủ của GitHub** (đã xác nhận: HTTP 403). Chợ Tốt thì không bị chặn nên đã chạy được trên máy GitHub. Nếu vẫn muốn có Batdongsan:
1. *Settings → Actions → Runners → New self-hosted runner*, làm theo hướng dẫn trên một máy ở Việt Nam (nên dùng Linux/macOS; Windows cần Git Bash). Máy phải bật lúc 08:37.
2. *Settings → Secrets and variables → Actions → Variables*: tạo biến `BDS_RUNNER` = `self-hosted` (hoặc nhãn riêng của runner).

Khi chưa đặt `BDS_RUNNER`, job Batdongsan vẫn thử trên máy GitHub và báo lỗi, nhưng không làm hỏng workflow.

---

## 4. Lấy dữ liệu lịch sử (backfill)

### 4.1. Tự động hoặc tuỳ chỉnh
**Không cần bấm gì:** nguồn nào chưa có kế hoạch sẽ tự ghi kế hoạch mặc định (cột "Mốc `auto`" bên dưới) ngay lần chạy đầu tiên, rồi các lượt sau tải dần lịch sử. Khi mốc `auto` trong code được dời sớm hơn, kế hoạch đang có tự mở rộng theo ở lượt kế tiếp (phần đã xong giữ nguyên). Muốn tắt, đặt biến `BACKFILL_AUTO=0`.

Muốn lấy xa hơn mốc mặc định hoặc chỉ một số nguồn: *Actions → Collect energy data* → **Run workflow**:

| Ô | Giá trị | Ý nghĩa |
|---|---|---|
| `backfill_start` | `auto` | Mỗi nguồn lấy từ mốc mặc định (bảng dưới) |
| | `2000-01-01` | Lấy từ ngày cụ thể (không sớm hơn mốc sớm nhất của nguồn) |
| `backfill_end` | *(trống)* | Đến hôm nay |
| `backfill_sources` | *(trống)* hoặc ví dụ `era5,nyiso_rt` | Chỉ backfill một số nguồn |

| Nguồn | Mốc `auto` | Mốc sớm nhất | Đơn vị chia phần | Dung lượng ước tính khi xong* |
|---|---|---|---|---|
| `era5` | 2015-01-01 | 1940-01-01 | năm × địa điểm | ~100 MB |
| `airquality` | 2022-08-01 | 2022-08-01 | năm × địa điểm | ~20 MB |
| `eia_bulk` (lưới điện 07/2015–12/2018, file CSV) | 2015-07-01 | 2015-07-01 | nửa năm | ~40 MB |
| `eia` (lưới điện theo giờ qua API, từ 2019) | 2019-01-01 | 2019-01-01 | tháng | ~100 MB |
| `eia_market` (giá nhiên liệu, bán lẻ) | 1986-01-01 | 1986-01-01 | năm | ~5 MB |
| `europe_power` | 2015-01-01 | 2015-01-01 | tháng × nước | ~180 MB |
| `europe_price` | 2015-01-01 | 2015-01-01 | tháng | ~10 MB |
| `gb` | 2016-01-01 | 2016-01-01 | tháng | ~10 MB |
| `aemo` | 1998-12-01 | 1998-12-01 | tháng | ~20 MB |
| `nyiso_da` | 2000-01-01 | 2000-01-01 | tháng | ~6 MB |
| `nyiso_rt` | 2000-01-01 | 2000-01-01 | tháng | ~6 MB |

\* **[Ước tính]** dung lượng nén, dựa trên kích thước thực đo của dữ liệu Open-Meteo và số dòng/cột dự kiến. Con số thật hiện trong `CATALOG.md`. Tổng nhóm năng lượng khoảng **0,5 GB**.

**Vì sao mốc `auto` không phải lúc nào cũng là mốc sớm nhất:**
- ERA5 được căn theo dữ liệu lưới điện (2015), vì thời tiết trước đó không có phụ tải để ghép; lấy từ 1940 sẽ tăng thêm khoảng 700 MB.

Muốn lấy xa hơn thì điền ngày cụ thể.

> Backfill đã chạy từ ngày 27/09/2026. Riêng ERA5 xong 175/264 phần ngay trong lượt đầu (95 phút).

### 4.2. Cách backfill chạy
- Kế hoạch lưu trong `data/energy/_backfill.json`. Mỗi lượt tải trong quỹ thời gian, commit sau mỗi nguồn, rồi **tự kích hoạt lượt tiếp** nếu chưa có lượt nào đang chờ (tối đa 40 lượt nối tiếp). Sau đó các lượt theo lịch làm tiếp đến khi xong.
- Theo dõi ở mục **Backfill progress** trong `data/energy/CATALOG.md`.
- Phần nào nguồn trả lỗi cố định (HTTP 400/404/422, hoặc không có file cho tháng đó) được đánh dấu **skipped**. Lỗi tạm thời (429, 5xx, mất kết nối) thì dừng và thử lại lượt sau.
- Chạy lại với khoảng rộng hơn sẽ **mở rộng** kế hoạch; phần đã xong không bị tải lại.

### 4.3. Thời gian dự kiến [ước tính]
Vài ngày cho toàn bộ. Yếu tố chậm nhất:
- **ERA5 và chất lượng không khí:** hạn mức Open-Meteo miễn phí (~10.000 lượt/ngày; một request dài nhiều biến tính thành nhiều lượt); 40 điểm × 12 năm ≈ 480 phần.
- **EIA qua API:** mỗi tháng khoảng 160 request (~15 phút) vì có đủ mọi vùng; ~93 tháng từ 2019 mất khoảng 1 ngày chạy nối tiếp. Phần 2015–2018 lấy từ file CSV nên nhanh hơn nhiều.
- **Energy-Charts:** 10 nước × 141 tháng.

---

## 5. Cấu trúc dữ liệu

```
data/
├── energy/
│   ├── CATALOG.md  _backfill.json  _catalog_cache.json
│   ├── weather/{era5, observed, forecast}/YYYY-MM.csv[.gz]
│   ├── airquality/observed/…
│   ├── eia/{region, fuel_type, interchange, subregion, fuel_prices, retail_sales}/…
│   ├── europe/{power, price}/…
│   ├── gb/{generation, demand, carbon_intensity}/…
│   ├── aemo/price_demand/…
│   └── nyiso/{lbmp_da, lbmp_rt}/…
└── realestate/
    ├── CATALOG.md
    ├── zillow/{zhvi_metro, zhvi_county, zori_metro, inventory_metro, sales_count_metro}/<bản mới nhất>.csv.gz
    ├── fhfa/hpi_master/<bản mới nhất>.csv.gz
    ├── realtor/inventory_metro/<bản mới nhất>.csv.gz
    ├── chotot/{ads, snapshots}/…
    └── batdongsan/{listings, details}/…
```

- **Tên file = tháng của cột thời gian** trong bảng. `forecast` theo `issued_at`; `snapshots`/`listings` theo ngày thu thập; `chotot/ads` theo `list_time`.
- `.csv` và `.csv.gz` cùng tồn tại trong một bảng. `pandas.read_csv` đọc cả hai.
- Giá trị rỗng được lưu thành chuỗi rỗng.

---

## 6. Từ điển dữ liệu (data dictionary)

### 6.1. Thời tiết — `energy/weather/{era5, observed, forecast}`, `energy/airquality/observed`

| Cột | Ý nghĩa |
|---|---|
| `location` | `<quốc gia>_<vùng lưới>_<thành phố>`, ví dụ `US_ERCO_Houston`, `AU_NSW1_Sydney`, `GB_London`, `DE_Berlin`, `VN_HoChiMinh` (40 điểm, xem `LOCATIONS` trong `weather_collector.py`) |
| `issued_at` | *(forecast)* thời điểm lấy bản dự báo |
| `time` | Giờ hiệu lực (UTC) |
| `temperature_2m`, `apparent_temperature`, `dew_point_2m` | °C |
| `relative_humidity_2m`, `cloud_cover` | % |
| `precipitation` | mm |
| `surface_pressure` | hPa |
| `wind_speed_10m`, `wind_speed_100m`, `wind_gusts_10m` | km/h |
| `wind_direction_100m` | độ |
| `shortwave_radiation`, `direct_normal_irradiance`, `diffuse_radiation` | W/m² (GHI, DNI, DHI) |
| *(airquality)* `pm10`, `pm2_5`, `nitrogen_dioxide`, `ozone`, `sulphur_dioxide`, `carbon_monoxide`, `us_aqi` | µg/m³, chỉ số AQI Mỹ |

Ba bảng thời tiết dùng cho ba mục đích:
- **`era5`**: tái phân tích chuẩn, trễ ~6 ngày. Dùng làm thời tiết thực tế.
- **`observed`**: giá trị phân tích của mô hình dự báo, vài ngày gần nhất.
- **`forecast`**: **mọi bản dự báo** kể từ ngày bắt đầu cào; phần này không backfill được. Dùng để đánh giá dự báo phụ tải bằng đúng thông tin thời tiết có sẵn tại thời điểm dự báo.

### 6.2. EIA — lưới điện Mỹ (dạng rộng, đơn vị MWh)

`period` là giờ UTC, theo quy ước của EIA là **thời điểm kết thúc giờ**: `2019-01-02T06:00Z` là giờ 05:00–06:00 UTC. Mình đã đối chiếu từng giá trị giữa API và file CSV 6 tháng để xác nhận quy ước này. Từ 2019 dữ liệu lấy qua API; 07/2015–12/2018 lấy từ file CSV 6 tháng của EIA (API không phục vụ giai đoạn này), ánh xạ vào cùng tên cột. Trong giai đoạn 2015–2018 chỉ có phát điện theo nhiên liệu từ 07/2018 và không có vùng con.


| Bảng | Tên cột | Ví dụ |
|---|---|---|
| `eia/region` | `<BA>_<type>`, type: `D` phụ tải · `DF` dự báo phụ tải ngày tới · `NG` phát điện ròng · `TI` trao đổi ròng | `ERCO_D`, `CISO_DF` |
| `eia/fuel_type` | `<BA>_<fuel>`, fuel: `SUN`, `WND`, `NG`, `COL`, `NUC`, `WAT`, `OIL`, `OTH`, `BAT`, … | `CISO_SUN` |
| `eia/interchange` | `<từ BA>><đến BA>` (dương = xuất sang) — **cạnh của đồ thị lưới điện** cho ST-GNN | `CISO>BPAT` |
| `eia/subregion` | `<BA cha>_<vùng con>` (vùng của PJM, vùng thời tiết của ERCOT, vùng của NYISO, …) | `ERCO_COAS`, `PJM_DOM` |

Danh sách mã BA: <https://www.eia.gov/electricity/gridmonitor/about>.

### 6.3. EIA — thị trường (dạng dài)

| Bảng | Cột |
|---|---|
| `eia/fuel_prices` | `period` (ngày), `series` (ví dụ `RWTC` WTI, `RBRTE` Brent, `RNGWHHD` Henry Hub), `description`, `area`, `units`, `value` |
| `eia/retail_sales` | `period` (tháng), `stateid`, `sectorid` (`RES`, `COM`, `IND`, `TRA`, `OTH`, `ALL`), `price` (cent/kWh), `revenue` (triệu USD), `sales` (triệu kWh), `customers` |

### 6.4. Châu Âu — `energy/europe/power`, `energy/europe/price`
- **`power`**: `timestamp`, `country` (`DE`, `FR`, `ES`, `IT`, `NL`, `BE`, `AT`, `PL`, `CH`, `DK`), sau đó mỗi loại nguồn một cột đúng tên do Energy-Charts công bố, ví dụ `Solar`, `Wind onshore`, `Wind offshore`, `Fossil gas`, `Nuclear`, `Hydro Run-of-River`, `Hydro pumped storage consumption`, `Cross border electricity trading`, `Load`, `Residual load`. Đơn vị MW, phần lớn là 15 phút.
- **`price`**: `timestamp` + mỗi vùng giá một cột (`DE-LU`, `FR`, `ES`, `NL`, `BE`, `AT`, `PL`, `CH`, `DK1`, `DK2`, `NO2`, `SE3`, `IT-North`). Đơn vị EUR/MWh.

### 6.5. Anh — `energy/gb/*` (30 phút)
- **`generation`**: mỗi loại nhiên liệu một cột (`CCGT`, `WIND`, `NUCLEAR`, `BIOMASS`, `COAL`, `NPSHYD`, `PS`, `OCGT`, `OIL`, `OTHER`, và các cột `INT*` là các đường dây liên kết quốc tế). Đơn vị MW.
- **`demand`**: `indo` (phụ tải quốc gia), `itsdo` (phụ tải hệ thống truyền tải). Đơn vị MW.
- **`carbon_intensity`**: `forecast`, `actual` (gCO2/kWh), `index` (very low … very high).

### 6.6. Úc — `energy/aemo/price_demand`
`timestamp` (UTC) + `<REGION>_demand` (MW), `<REGION>_price` (AUD/MWh) cho `NSW1`, `QLD1`, `VIC1`, `SA1`, `TAS1`. Khoảng đo 30 phút trước 10/2021, 5 phút sau đó. Riêng nguồn này, `timestamp` là **thời điểm kết thúc** của khoảng đo (quy ước của AEMO), đã đổi sang UTC.

### 6.7. New York — `energy/nyiso/lbmp_da`, `lbmp_rt`
`timestamp` (UTC, thời điểm bắt đầu) + mỗi vùng tải một cột: `CAPITL`, `CENTRL`, `DUNWOD`, `GENESE`, `H Q`, `HUD VL`, `LONGIL`, `MHK VL`, `MILLWD`, `N.Y.C.`, `NORTH`, `WEST`, `NPX`, `O H`, `PJM`. Giá LBMP tính bằng $/MWh; cả `da` và `rt` đều theo giờ (file vùng của NYISO công bố giá thời gian thực đã tích hợp theo giờ; đã kiểm tra trên dữ liệu thật).

### 6.8. Bất động sản Mỹ — `realestate/{zillow, fhfa, realtor}/*`
Mỗi thư mục chỉ giữ **bản phát hành mới nhất**, và bản này đã chứa toàn bộ lịch sử; tên file là kỳ dữ liệu mới nhất.
- **Zillow** (dạng rộng, mỗi tháng một cột): `zhvi_*` chỉ số giá nhà (từ 2000), `zori_metro` chỉ số giá thuê (từ 2015), `inventory_metro` tồn kho rao bán, `sales_count_metro` số giao dịch (từ 2008).
- **FHFA** `hpi_master`: chỉ số giá nhà theo quốc gia, bang, vùng đô thị (các cột `hpi_type`, `hpi_flavor`, `frequency`, `level`, `place_name`, `place_id`, `yr`, `period`, `index_nsa`, `index_sa`).
- **Realtor.com** `inventory_metro`: giá niêm yết trung vị, số tin đang rao, số ngày trên thị trường, số tin mới, số tin tăng/giảm giá theo vùng đô thị và tháng (từ 2016).

### 6.9. Chợ Tốt — `realestate/chotot/ads`, `snapshots`

| Cột (`ads`) | Ý nghĩa |
|---|---|
| `list_id`, `ad_id` | Mã tin (khoá: `list_id`) |
| `list_time` | Thời điểm đăng hoặc đẩy tin (UTC) |
| `scraped_at` | Lần thu thập gần nhất |
| `category` | `1010` căn hộ, `1020` nhà, `1040` đất |
| `type` | `s` bán, `k` cần mua |
| `region_name`, `area_name`, `ward_name`, `street_name`, `pty_project_name` | Tỉnh, quận, phường, đường, dự án |
| `latitude`, `longitude` | Toạ độ |
| `price`, `price_million_per_m2` | Giá (VNĐ), đơn giá (triệu/m²) |
| `size`, `living_size`, `width`, `length` | Diện tích đất, diện tích sử dụng (m²), chiều ngang, chiều dài (m) |
| `rooms`, `toilets`, `floors` | Số phòng ngủ, WC, tầng |
| `direction`, `house_type`, `apartment_type`, `property_legal_document`, `furnishing_sell`, `is_main_street`, `pty_characteristics` | Mã hoá theo Chợ Tốt; nhãn tiếng Việt tương ứng nằm trong `params` |
| `params` | JSON `{mã thuộc tính: nhãn}`, ví dụ `{"direction": "Hướng Bắc"}` |
| `company_ad` | Tin của môi giới hoặc doanh nghiệp |
| `subject`, `body` | Tiêu đề, 500 ký tự đầu của mô tả; đã che số điện thoại |

`snapshots`: `list_id`, `price`, `scraped_date`, mỗi tin một dòng mỗi ngày. Dùng để tính biến động giá và thời gian tin tồn tại trên sàn.

**Không lưu** bất kỳ thông tin nhận diện người đăng nào (tên, tài khoản, ảnh đại diện, điện thoại).

### 6.10. Batdongsan — `realestate/batdongsan/{listings, details}`
`listings`: `listing_id`, `scraped_date`, `category`, `city`, `title`, `price_text`, `price_vnd`, `area_m2`, `bedrooms`, `toilets`, `location`, `is_vip`, `url`, … `details`: `latitude`, `longitude`, `address`, `description`, `posted_date`, `specs_json`, …

---

## 7. Chạy trên máy cá nhân

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python -m scrapers.energy.europe_collector            # không cần key
export EIA_API_KEY=...                                # PowerShell: $env:EIA_API_KEY="..."
BACKFILL_START=2020-01-01 BACKFILL_SOURCES=eia BACKFILL_MINUTES=60 python -m scrapers.energy.eia_collector
python scripts/build_catalog.py energy
python -m pytest -q                                   # test offline, không gọi mạng
```

| Biến môi trường | Mặc định | Tác dụng |
|---|---|---|
| `BACKFILL_START` / `BACKFILL_END` / `BACKFILL_SOURCES` | trống | Như mục 4.1 |
| `BACKFILL_AUTO` | 1 | `0` = không tự ghi kế hoạch backfill cho nguồn mới |
| `BACKFILL_MINUTES` | 90 (workflow đặt 15–85 tuỳ bước) | Quỹ thời gian backfill của một collector trong một lượt |
| `OPEN_METEO_PAUSE_SECONDS` | 30 | Nghỉ giữa các request lịch sử Open-Meteo |
| `WEATHER_PAST_DAYS` / `WEATHER_FORECAST_DAYS` | 3 / 2 | Cửa sổ gần đây của Open-Meteo |
| `EIA_LOOKBACK_DAYS` | 7 | |
| `CHOTOT_MAX_PAGES` / `CHOTOT_BODY_CHARS` | 40 / 500 | Số trang (50 tin/trang) mỗi truy vấn; số ký tự mô tả được lưu (0 = không lưu) |
| `BDS_MAX_PAGES` / `BDS_DETAIL_LIMIT` | 5 / 80 | |

---

## 8. Đọc dữ liệu để phân tích

```python
from pathlib import Path
import pandas as pd

def load(table, **kw):
    files = sorted(Path("data", table).glob("*.csv*"))   # đọc cả .csv và .csv.gz
    return pd.concat((pd.read_csv(f, **kw) for f in files), ignore_index=True)

def hourly(table, time_col):
    df = load(table)
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    return df.set_index(time_col).sort_index()

# Phụ tải toàn bộ vùng lưới Mỹ: mỗi cột một BA
region = hourly("energy/eia/region", "period")
demand = region.filter(regex="_D$")

# Đồ thị lưới điện cho ST-GNN: nút = BA, cạnh = cặp có trao đổi điện
flows = hourly("energy/eia/interchange", "period")
edges = [tuple(c.split(">")) for c in flows.columns]

# Ghép thời tiết ERA5 Houston vào phụ tải ERCOT
wx = load("energy/weather/era5")
wx = wx[wx.location == "US_ERCO_Houston"].assign(time=lambda d: pd.to_datetime(d.time, utc=True)).set_index("time")
ercot = region[["ERCO_D", "ERCO_DF"]].join(wx[["temperature_2m", "shortwave_radiation"]], how="inner")

# Đức: phụ tải, mặt trời, gió và giá ngày tới
de = hourly("energy/europe/power", "timestamp").query("country == 'DE'")[["Load", "Solar", "Wind onshore"]]
de = de.join(hourly("energy/europe/price", "timestamp")[["DE-LU"]], how="left")

# Giá điện NSW (Úc) theo 30 phút
nsw = hourly("energy/aemo/price_demand", "timestamp")[["NSW1_demand", "NSW1_price"]].resample("30min").mean()

# Dự báo thời tiết phát hành trước thời điểm t tối thiểu 24h (tránh rò rỉ thông tin tương lai)
fc = load("energy/weather/forecast")
fc[["time", "issued_at"]] = fc[["time", "issued_at"]].apply(pd.to_datetime, utc=True)
fc = fc[(fc.time - fc.issued_at) >= pd.Timedelta("24h")].sort_values("issued_at").groupby(["location", "time"]).last()

# Chợ Tốt: giá/m² theo quận và thời gian tin tồn tại
ads = load("realestate/chotot/ads").sort_values("list_time").drop_duplicates("list_id", keep="last")
snap = load("realestate/chotot/snapshots")
days_listed = snap.groupby("list_id").scraped_date.agg(["min", "max", "count"])
```

Khi chỉ cần một nhóm dữ liệu, có thể clone nông và thưa:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/sweetluvz/Collectdata.git
cd Collectdata && git sparse-checkout set data/energy/eia
```

### 8.1. Xử lý sơ bộ (`processing/`)

Dữ liệu thô giữ nguyên như nguồn công bố. `processing/` sinh ra **bảng phân tích theo giờ** cho từng vùng lưới
và bảng tin Chợ Tốt đã làm sạch, ghi vào `processed/` (không commit; chạy lại khi cần, vài phút trên CPU).

```bash
pip install -r requirements.txt
python -m processing.build us --areas ERCO,CISO,PJM --start 2019-01-01   # mặc định 16 BA lớn
python -m processing.build europe --areas DE,FR                           # mặc định 10 nước
python -m processing.build aemo
python -m processing.build chotot
python -m processing.build all                                            # tất cả, vùng mặc định
```

| Đầu ra | Nội dung (mỗi dòng = 1 giờ, UTC, **nhãn cuối giờ**: `01:00Z` = 00:00–01:00) |
|---|---|
| `processed/us/<BA>.csv.gz` | `demand_raw`, `demand` (đã sàng lọc + nội suy khoảng trống ≤ 3 h), `demand_flags`, `eia_dayahead_forecast` (dự báo ngày tới của chính BA — mốc so sánh vận hành), `net_generation`, `interchange`, thời tiết ERA5 `wx_*` (trung bình các điểm của BA), `local_hour/dow/month`, `us_holiday` |
| `processed/europe/<CC>.csv.gz` | các cột Energy-Charts `ec_*` gộp từ 15 phút về giờ (MW; cột `share` là %), `load` (đã sàng lọc), `load_flags`, `price_eur_mwh` (vùng giá tương ứng, **không** sàng lọc: giá âm/cực trị là thật), `wx_*`, lịch |
| `processed/aemo/<REGION>.csv.gz` | `demand_raw`, `demand`, `demand_flags`, `price_aud_mwh`, `wx_*`, lịch (giờ Brisbane) |
| `processed/chotot/ads_clean.csv.gz` | tin bán đã khử trùng, `price_per_m2`, `city`, `category_name`, `first_seen`/`last_seen`/`days_seen` |
| `processed/quality.csv`, `QUALITY.md` | báo cáo chất lượng: số giờ, % thiếu, khoảng thiếu dài nhất, số điểm bị gắn cờ theo từng phép kiểm tra |

**Chuẩn hoá thời gian.** Mỗi nguồn gán nhãn khác nhau (mục 6): EIA và AEMO theo *cuối* khoảng, Energy-Charts,
Elexon, NYISO theo *đầu* khoảng. `processing.io.to_hourly_end()` đưa tất cả về nhãn cuối giờ. Đã kiểm tra trên
dữ liệu thật: phụ tải ERCOT đạt đỉnh 17h, CAISO 18h giờ địa phương, bức xạ đạt đỉnh 12–13h.

**Sàng lọc** (`processing/clean.py`), đơn giản hơn nhiều so với Ruggles et al. (2020), *Sci. Data* 7:155:

| Cờ | Điều kiện |
|---|---|
| `nonpositive` | giá trị ≤ 0 |
| `stuck` | cùng một giá trị lặp ≥ 24 giờ liên tiếp (telemetry đóng băng) |
| `level` | lệch > 10 lần so với trung vị trượt 4 tuần |
| `spike` | vọt khỏi **cả hai** giờ lân cận cùng chiều, lớn hơn 8 lần độ biến thiên giờ-giờ điển hình (MAD); dốc tăng/giảm đơn điệu không bị gắn cờ |

Điểm bị gắn cờ → NaN; khoảng trống ≤ `--max-gap` giờ (mặc định 3) nội suy tuyến tính; khoảng dài hơn để NaN
để người dùng tự quyết (bỏ, hay bù bằng mô hình). Cột `*_raw` và `*_flags` giữ lại để mọi thay đổi đều kiểm
tra được. AEMO: `nonpositive` và vế dưới của `level` bị tắt vì phụ tải vận hành của SA1/VIC1 xuống gần 0 hoặc âm
vào buổi trưa do điện mặt trời áp mái — đó là giá trị thật (đã thấy −44 MW ở SA1 tháng 9/2026).

**Chợ Tốt** (`processing/realestate.py`): mỗi tin bị loại được ghi lý do — `not_for_sale`, `no_price`, `no_size`,
`price_per_m2_implausible` (ngoài 1 triệu–1 tỷ VND/m²), `no_coordinates`, `price_per_m2_outlier` (|log giá/m² − trung
vị| > 4·MAD trong từng thành phố × loại BĐS). Lần chạy 27/09/2026: 9.424 tin → giữ 9.020.

> Các ngưỡng trên là lựa chọn thực dụng, **chưa được hiệu chỉnh** trên dữ liệu có nhãn lỗi. Khi viết báo, hãy
> báo cáo `QUALITY.md`, thử độ nhạy của kết quả với ngưỡng, và trích Ruggles et al. (2020) nếu dùng bộ EIA-930 đã
> được họ làm sạch để đối chiếu.

---

## 9. Giám sát & bảo trì

| Việc | Cách làm |
|---|---|
| Biết khi có lỗi | Job *failed* → GitHub gửi email. Bật trong *Settings (tài khoản) → Notifications → Actions* |
| Dữ liệu có vào đều không | Cột **To** trong `data/*/CATALOG.md` |
| Tiến độ backfill | Mục **Backfill progress** trong `data/energy/CATALOG.md` |
| Backfill dừng lâu | Xem log bước tương ứng: `will retry next run` (lỗi tạm thời) hay `skipped`. Có thể bấm Run workflow (để trống các ô) để chạy tiếp ngay |
| Workflow bị tắt | `keepalive.yml` bật lại hằng tuần; nếu vẫn *disabled* thì bấm *Enable workflow* |
| Lỗi `HTTP 4xx ... <thông báo>` | Đọc thông báo API trong log. Với EIA thường do key: tạo key mới và cập nhật secret |
| Chợ Tốt hoặc Batdongsan trả 0 tin | API hoặc HTML đổi. Sửa `chotot_collector.py` / `batdongsan_collector.py` và dữ liệu mẫu trong `tests/` |
| Làm lại một phần backfill | Xoá mã phần đó khỏi `done`/`skipped` trong `_backfill.json`, commit, chạy workflow |
| Cập nhật thư viện | Sửa `requirements.txt` (đang pin cố định), chạy `pytest`, push |

---

## 10. Tuỳ biến

| Muốn thay đổi | Sửa ở đâu |
|---|---|
| Điểm thời tiết | `LOCATIONS` trong `weather_collector.py`; chạy lại backfill `era5` để lấy lịch sử cho điểm mới |
| Nước / vùng giá châu Âu | `COUNTRIES`, `BIDDING_ZONES` trong `europe_collector.py` |
| Chuỗi giá EIA, bảng thị trường khác của EIA | `MARKET` trong `eia_collector.py` (route theo <https://www.eia.gov/opendata/browser/>) |
| Loại BĐS, thành phố Chợ Tốt | `CATEGORIES`, `REGIONS` trong `chotot_collector.py` |
| Bộ dữ liệu nhà ở Mỹ | `DATASETS` trong `us_housing_collector.py` |
| Tần suất chạy | Dòng `cron:` trong `.github/workflows/*.yml` |
| Thêm nguồn có backfill | Gọi `backfill.run(...)` trong collector và thêm tên nguồn vào `SOURCES` trong `utils/backfill.py` |

---

## 11. Giới hạn & rủi ro đã biết

**Nguồn đã loại hoặc không dùng được (không miễn phí, cần duyệt, hoặc không truy cập được)**
- **ENTSO-E** (cần email xin duyệt token): đã thay bằng Energy-Charts.
- **Sáng chế:** PatentsView và Lens cần key; bộ tải hàng loạt của PatentsView nay chuyển sang cổng USPTO và cần tài khoản (đã kiểm tra: HTTP 403). Hướng nghiên cứu sáng chế hiện **không có nguồn miễn phí tự động**.
- **FRED:** quá thời gian chờ khi truy cập từ máy GitHub (đã thử 2 lần).
- **Redfin, Zillow cấp mã bưu chính:** miễn phí nhưng mỗi file 110–240 MB, quá lớn để lưu trong git.

**Không thể lấy lịch sử**
- **Chợ Tốt, Batdongsan:** chỉ có tin đang hiển thị; dữ liệu bắt đầu từ ngày cào.
- **Bản dự báo thời tiết** (`forecast`): chỉ có từ ngày bắt đầu cào.

**Dung lượng & hạn mức**
- Sau backfill mặc định, repo **khoảng 0,5–0,7 GB** [ước tính], rồi tăng thêm khoảng 100–200 MB/năm, chủ yếu do Chợ Tốt và dữ liệu năm mới. GitHub khuyến nghị repo dưới 1 GB. Mỗi workflow chỉ checkout thư mục nhóm của mình. Khi vượt 1 GB, nên chuyển dữ liệu cũ sang Hugging Face Datasets hoặc Zenodo (Zenodo có DOI để trích dẫn).
- Open-Meteo miễn phí: khoảng 10.000 lượt/ngày, một request dài được tính thành nhiều lượt [cách tính chính xác chưa xác minh], nên backfill ERA5 kéo dài vài ngày.
- Hạn mức gọi API của Energy-Charts, Elexon, AEMO, NYISO, Chợ Tốt không được công bố rõ. Code giãn cách 0,5–2 giây/request và tự thử lại khi gặp 429/5xx.

**Kỹ thuật**
- Chợ Tốt dùng API nội bộ của trang (không có tài liệu chính thức), có thể đổi bất cứ lúc nào. Mỗi truy vấn tối đa 10.000 tin (đã xác nhận).
- Selector HTML của Batdongsan sẽ hỏng khi trang đổi giao diện.
- `keepalive.yml`: việc bật lại workflow có reset bộ đếm 60 ngày hay không thì chưa được xác minh; các commit dữ liệu thường xuyên cũng giữ repo hoạt động.

**Tính hợp lệ của dữ liệu cho nghiên cứu**
- **Chợ Tốt và Batdongsan là giá chào bán, không phải giá giao dịch.** Mẫu thiên về tin mới và tin được đẩy lên đầu (selection bias). Tin biến mất khỏi `snapshots` không có nghĩa là đã bán.
- Chợ Tốt và Batdongsan có thể trùng tin (cùng người đăng trên hai sàn); cần khử trùng theo toạ độ, diện tích và giá nếu gộp hai nguồn.
- ERA5 là tái phân tích trên lưới khoảng 25–30 km, không phải số đo trạm.
- EIA-930 có các khoảng thiếu và giá trị bất thường; nên làm sạch trước khi dùng, ví dụ theo quy trình sàng lọc và bù dữ liệu của Ruggles et al. (2020), *Developing reliable hourly electricity demand data through screening and imputation*, Scientific Data 7:155.
- Energy-Charts tổng hợp từ ENTSO-E và nguồn quốc gia; định nghĩa `Load` có thể khác nhau giữa các nước.

**Quyền riêng tư & giấy phép** (repo đang **public**)
- Không lưu thông tin nhận diện người đăng; số điện thoại trong văn bản được thay bằng `[SĐT]`. Phần mô tả tự do vẫn có thể chứa tên người; cần rà soát trước khi công bố bộ dữ liệu, hoặc chuyển repo sang private.
- Cần ghi nguồn khi công bố: EIA (public domain); Open-Meteo và Energy-Charts (CC BY 4.0); Elexon BMRS (BSC Open Data Licence); NESO Carbon Intensity (CC BY 4.0); AEMO, NYISO, Zillow, FHFA, Realtor.com (theo điều khoản của từng nguồn). Chợ Tốt và Batdongsan: chỉ dùng cho nghiên cứu, tuân thủ điều khoản của trang.

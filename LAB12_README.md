# Lab 12 — Cloud Services & Deployment: Từ Code Đến Production

## Bức tranh toàn cảnh & Thuật ngữ
Một ứng dụng AI chạy được trên máy không có nghĩa nó sẵn sàng cho người dùng thật. Khoảng cách từ 'chạy được' đến 'chạy ổn định trên cloud' chính là nội dung bài lab này.

Bạn sẽ đưa một AI Agent (dùng mock LLM — không cần API key bên ngoài) từ code chạy trên laptop lên production trên cloud, qua 5 tầng bảo vệ:
1. **12-Factor Config**
2. **Docker Multi-stage**
3. **API Security** (Auth + Rate Limit + Cost Guard)
4. **Stateless + Scale** (Stateless + Redis + Scale ngang)
5. **Cloud Deploy**

> [!NOTE]
> Lab dùng mock LLM chạy offline — không cần API key OpenAI hay bất kỳ bên cung cấp LLM nào. Mỗi block có bộ test riêng.

### Bảng thuật ngữ trực quan
| Thuật ngữ | Bản chất | Minh hoạ trong lab |
|---|---|---|
| **12-Factor App** | 12 nguyên tắc thiết kế ứng dụng cloud-native | Cấu hình qua biến môi trường (`.env`), không hardcode. App chết ngay nếu thiếu key quan trọng (fail-fast) thay vì chạy sai âm thầm. |
| **Docker Multi-stage Build** | Đóng gói 2 giai đoạn: build rồi mới copy kết quả | Stage 1 cài dependencies (~1GB), Stage 2 chỉ copy file cần thiết → image production nhỏ gọn (~150MB). |
| **Non-root Container** | Container chạy bằng user thường, không phải root | Cắt đứt chuỗi tấn công leo thang hệ thống nếu có lỗ hổng code. |
| **Rate Limit (Sliding Window)** | Giới hạn số request/phút bằng cửa sổ trượt | Dùng Redis Sorted Set đếm request trong 60 giây gần nhất. Vượt hạn mức → trả HTTP 429. |
| **Cost Guard** | Ngân sách tối đa/tháng cho mỗi user | Tích lũy chi phí token. Vượt budget → trả HTTP 402 (Payment Required). |
| **Graceful Shutdown** | Tắt máy chủ từ từ, không cắt ngang request | Nhận tín hiệu SIGTERM: ngừng nhận request mới, đợi request đang chạy hoàn thành rồi mới tắt. |
| **Stateless** | App không lưu state trong RAM | Lịch sử hội thoại lưu trong Redis thay vì dict Python, giúp dễ scale ngang ra nhiều container. |
| **Health Check** | `Liveness /health` và `Readiness /ready` | `/health` luôn 200 khi process sống. `/ready` trả 503 khi Redis mất hoặc đang shutdown. |
| **CI/CD** | Tự động test + build + deploy | GitHub Actions chạy pytest, build Docker image, và deploy lên cloud không cần gõ lệnh thủ công. |

### Bảng chấm điểm nhanh (100 điểm)
| Checkpoint | Nội dung | Điểm |
|---|---|---|
| CP1 | 12-Factor Config, Health & Logging | 15 |
| CP2 | Docker: multi-stage, bảo mật image | 15 |
| CP3 | API Security: auth, rate limit, cost guard | 20 |
| CP4 | Scaling & Reliability | 20 |
| CP5 | Cloud Deployment | 15 |
| exercises.md | 10 câu phản ánh | 15 |
| **Tổng** | | **100** |
| *BONUS* | CI/CD với GitHub Actions | *+10* |

---

## Yêu cầu chi tiết theo Checkpoint

### CP0 - Setup môi trường (0:00–0:20)
1. Fork repo Github tương ứng (K3 hoặc K4) và Clone về máy:
   ```bash
   git clone https://github.com/<username>/K3-Day12-Cloud-Services-And-Deployment.git
   cd K3-Day12-Cloud-Services-And-Deployment
   ```
2. Tạo môi trường ảo (venv) và cài dependencies: `pip install -r requirements.txt`.
3. Tạo file cấu hình: `cp .env.example .env`. 
   - Đổi `AGENT_API_KEY` thành khóa tạo ngẫu nhiên (`python -c "import secrets; print(secrets.token_urlsafe(32))"`).
   - **Tuyệt đối không commit file `.env`**.
4. Khởi động Redis bằng Docker: `docker compose up -d redis` (hoặc `REDIS_URL=fake://`).
5. **Kiểm tra**: Chạy `pytest tests/test_cp1.py tests/test_cp2.py tests/test_cp3.py tests/test_cp4.py -v -m "not docker"`. Không có lỗi ModuleNotFoundError hoặc ImportError.

---

### CP1 - 12-Factor Config, Health & Logging (0:20–1:00)
1. **Settings (`app/config.py`)**: Sử dụng Pydantic `BaseSettings` để đọc cấu hình từ file `.env` với các biến: `port`, `agent_api_key` (bắt buộc, fail-fast), `redis_url`, `rate_limit_per_minute`, `monthly_budget_usd`, `log_level`.
2. **Structured Logging (`app/logging_utils.py`)**: Thay thế lệnh print bằng format log dạng JSON để dễ dàng parse bằng máy.
3. **Health & Readiness Endpoints (`app/main.py`)**:
   - `GET /health` (Liveness): Báo process đang chạy (200). Không gọi Redis.
   - `GET /ready` (Readiness): Trả về 200 nếu sẵn sàng nhận request (kết nối Redis OK). Trả về 503 khi Redis lỗi hoặc đang Graceful Shutdown.
4. **Kiểm tra**: `pytest tests/test_cp1.py -v` - Pass tất cả.

---

### CP2 - Docker: Multi-stage Build & Bảo mật Image (1:00–1:45)
1. **Multi-stage Build (`Dockerfile`)**: Tách làm 2 stage. Stage 1 (builder) để cài requirements. Stage 2 (production) chạy `python:3.11-slim`, chỉ copy thư mục cài đặt (`/usr/local`) từ builder sang.
2. **Bảo mật (Non-root user)**: Container phải chạy dưới quyền user thường (ví dụ: `appuser`) chứ không chạy quyền root.
3. **Healthcheck trong Dockerfile**: Tạo Python script dùng thư viện có sẵn (không cài curl) để ping `/health`.
4. **.dockerignore**: Bổ sung `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.git/`, `screenshots/`.
5. **Cập nhật `docker-compose.yml`**: Thêm service `agent` phụ thuộc vào `redis` (`condition: service_healthy`), không public port ra host trực tiếp mà trỏ qua nginx.
6. **Kiểm tra**: Build image `docker build -t day12-agent:prod .`, dung lượng dưới 500MB. Chạy `pytest tests/test_cp2.py -v`.

---

### CP3 - API Security: Auth, Rate Limit & Cost Guard (1:55–2:40)
1. **Xác thực API Key (`app/auth.py`)**: Validate `X-API-Key` trong Header. Nếu sai trả 401 Unauthorized.
2. **Rate Limit - Sliding Window (`app/rate_limiter.py`)**: Giới hạn tốc độ bằng thuật toán Sliding Window trên Redis (Sorted Set). Đếm số request trong 60 giây. Nếu vượt quota trả về mã HTTP 429.
3. **Cost Guard (`app/cost_guard.py`)**: Tính tiền mỗi lần gọi LLM (Pre-check và Post-record). Lưu chi phí tích lũy theo user. Nếu vượt quá budget trả về mã HTTP 402 Payment Required.
4. **Kiểm tra**: `pytest tests/test_cp3.py -v` - Pass tất cả.

---

### CP4 - Scaling & Reliability (2:40–3:20)
1. **Redis History Store (`app/store.py`)**: Dùng `rpush` và `lrange` để lưu và truy xuất lịch sử hội thoại lên Redis. App không còn lưu state trong RAM (Python Dict).
2. **Graceful Shutdown (`app/lifecycle.py`)**: Xử lý tín hiệu SIGTERM. /ready phải trả 503 ngay lập tức để ngừng nhận request, đợi tối đa 30s xử lý nốt các request đang chạy rồi đóng kết nối Redis an toàn.
3. **Kiểm tra Scale**: `docker compose up -d --scale agent=3`. Chạy 5 POST `/ask` liên tục thấy `history_length` tăng tuần tự từ 1->5, chứng tỏ history chia sẻ đúng đắn qua Redis.
4. **Kiểm tra**: `pytest tests/test_cp4.py -v` - Pass tất cả.

---

### CP5 - Deploy lên Cloud & Nộp bài (3:20–4:00)
1. Deploy mã nguồn lên nền tảng **Railway** hoặc **Render**.
2. **Bằng chứng bắt buộc (Required Evidence)**:
   - Ảnh chụp dashboard Cloud hiển thị Deploy thành công -> lưu vào thư mục `screenshots/`.
   - Các API `/health` (200), `/ready` (200), `/ask` (không key -> 401), `/ask` (có key -> 200) phải live.
   - (Trường hợp quá hạn mức Cloud, có thể dùng `LOCAL_FALLBACK=true` chạy trên máy cá nhân).
3. Điền URL public vào file `DEPLOYMENT.md`.
4. Trả lời đầy đủ 10 câu hỏi trong `exercises.md`.
5. Đảm bảo cấu trúc nộp bài: Đổi tên thư mục thành định dạng `KX-DAY12-[MSSV]-[HoVaTen]`.

---

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Chạy `pytest tests/test_cp1.py tests/test_cp2.py tests/test_cp3.py tests/test_cp4.py -v` pass hết (biết lỗi nếu rớt).
- [ ] Chạy `python grade.py` đạt tối thiểu ≥ 75/100.
- [ ] File `exercises.md` trả lời đủ 10 câu.
- [ ] File `DEPLOYMENT.md` có chứa Public URL thật (hoặc LOCAL_FALLBACK).
- [ ] Thư mục `screenshots/` có chứa hình ảnh chụp dashboard deploy.
- [ ] **TUYỆT ĐỐI KHÔNG** commit file `.env` lên repo.
- [ ] Tên thư mục format chuẩn `KX-DAY12-[MSSV]-[HoVaTen]`.
- [ ] Commit lịch sử nhiều lần, không gom chung thành 1 cục duy nhất.

---

### BONUS — CI/CD với GitHub Actions (Không bắt buộc, +10 điểm)
- Viết file `.github/workflows/ci.yml`.
- Tự động chạy Pytest, Build Docker Image, và Deploy.
- Phải dùng secret (không hardcode key trong file YAML) và mock biến môi trường.
- Đính kèm badge CI/CD vào repo README.md.
- Kiểm tra bằng `pytest tests/test_bonus_cicd.py -v`.

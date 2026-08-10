# Báo cáo Checkpoint 2
**MSSV:** 2A202601103 - NguyenDucNamKhanh

## Các thay đổi đã thực hiện:
1. **`Dockerfile`**:
   - Chuyển sang cấu trúc **Multi-stage build**:
     - `builder` stage: Cài đặt thư viện Python (`pip install`) với base image `python:3.11-slim`.
     - `runtime` stage: Chỉ copy các thư viện đã được biên dịch từ `builder` stage sang `/usr/local` nhằm giảm đáng kể kích thước image, bỏ lại các công cụ build.
   - Sắp xếp lại thứ tự lệnh: Copy `requirements.txt` và chạy `pip install` trước, tiếp theo mới copy mã nguồn (COPY . .). Điều này giúp tối ưu hoá caching của Docker layer, ngăn việc cài lại thư viện mỗi khi có thay đổi code.
   - Bảo mật: Tạo một `appuser` bằng lệnh `RUN useradd ...` và chuyển qua user đó để thực thi bằng lệnh `USER appuser`. Ngăn ngừa rủi ro chạy container bằng quyền root (bảo mật tối thiểu).
   - Thiết lập `HEALTHCHECK` kiểm tra liveness qua `/health`.
   - Ứng dụng đọc dynamic PORT thông qua biến môi trường (nếu không có thì mặc định port 8000).

2. **`.dockerignore`**:
   - Thêm `.env`, `.venv`, `__pycache__` và `*.pyc` vào danh sách loại trừ để bảo vệ các tệp mật, tệp môi trường cục bộ và các thư mục rác không bị đưa vào Docker image.

3. **`docker-compose.yml`**:
   - Thêm service `agent`:
     - Tự động lấy biến `$AGENT_API_KEY` từ file `.env` ngoài môi trường đưa vào.
     - Tham chiếu `REDIS_URL` thông qua hostname nội bộ `redis:6379`.
     - Đặt quan hệ phụ thuộc vào service `redis` bằng `depends_on`.
     - Thêm cơ chế `healthcheck` thông qua lệnh curl định kỳ.

## Kết quả kiểm thử:
- Test `pytest tests/test_cp2.py -v` đã thành công tất cả (trừ các bài test build docker image cụ thể do bỏ qua `docker build` cục bộ nhưng đã pass toàn bộ structural checks).

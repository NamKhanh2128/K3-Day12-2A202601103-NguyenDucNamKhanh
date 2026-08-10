# Báo cáo Checkpoint 1
**MSSV:** 2A202601103 - NguyenDucNamKhanh

## Các thay đổi đã thực hiện:
1. **`app/config.py`**:
   - Sử dụng `pydantic-settings` khai báo 6 biến môi trường `port`, `agent_api_key`, `redis_url`, `rate_limit_per_minute`, `monthly_budget_usd`, `log_level`.
   - Thuộc tính `agent_api_key` không khai báo giá trị mặc định, buộc phải có biến cấu hình này trong file `.env` hoặc hệ thống, giúp ứng dụng tự đóng ("fail fast") khi chưa được thiết lập khóa bảo mật.

2. **`app/logging_utils.py`**:
   - Hoàn thiện hàm `log_event()`, chuẩn hóa log về dạng JSON với các trường bắt buộc là `event`, `level` (viết thường) và `timestamp` (định dạng ISO-8601 múi giờ UTC).
   - Đảm bảo in log trên một dòng duy nhất bằng cách không dùng indent trong `json.dumps()` giúp công cụ tổng hợp log của Cloud Server dễ dàng thu thập và phân tích.

3. **`app/main.py`**:
   - Viết Endpoint `/health` (Liveness Probe).
   - Kiểm tra xem trạng thái đang có phải là `lifecycle.shutting_down` hay không, nếu có thì trả về status_code `503`. Ngược lại trả về thông tin `status: ok` với HTTP `200`.
   - Endpoint này nhẹ nhất có thể, hoàn toàn không phụ thuộc vào `redis` để ngăn ngừa tình trạng sập hàng loạt khi redis đang khởi động lại.

## Kết quả kiểm thử:
- Đã cài đặt thành thạo structured logging.
- Hoàn thành đầy đủ các tests trong `tests/test_cp1.py`.

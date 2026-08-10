# Báo cáo Checkpoint 4
**MSSV:** 2A202601103 - NguyenDucNamKhanh

## Các thay đổi đã thực hiện:
1. **`app/store.py` (Stateless Session)**:
   - Thay vì sử dụng dictionary trên RAM (`{}`), thay đổi kiến trúc để sử dụng **Redis** lưu trữ hội thoại của người dùng giúp hệ thống duy trì được tính *stateless*.
   - Khởi tạo hàm `append()`:
     - Dùng lệnh `rpush` ghi chuỗi JSON (chứa `role` và `content`) vào danh sách Redis list tại key của `user_id`.
     - Gọi `ltrim` để duy trì tối đa `HISTORY_MAX_MESSAGES` message gần nhất.
     - Thiết lập vòng đời `HISTORY_TTL_SECONDS` qua `expire` tránh cho RAM của Redis bị đầy dần do tích trữ vô hạn.
   - Khởi tạo hàm `get_history()`: Lấy ra mảng lịch sử từ Redis thông qua `lrange` và parse trở lại dictionary qua `json.loads`.
   - Hàm `ping()` trả về trạng thái của Redis (có sống không), không ném ra exception nếu sập.

2. **`app/lifecycle.py` (Graceful Shutdown)**:
   - Bắt các tín hiệu kết thúc từ hệ điều hành / Orchestrator (`SIGTERM` / `SIGINT`).
   - Cài đặt `request_shutdown` để đánh dấu cờ `shutting_down = True` báo cho hệ thống biết chuẩn bị tắt nhưng không dừng ngay để xử lý các request đang dở dang.
   - Gọi lại các signal handler mặc định của uvicorn để đảm bảo tiến trình tiếp tục tắt một cách an toàn mà không bị kẹt.

3. **`app/main.py` (/ready)**:
   - Endpoint `/ready` hoàn chỉnh kiểm tra *liveness* và *readiness*. Trả về lỗi 503 khi service đang shutdown hoặc khi Redis không thể ping (tránh cho proxy điều hướng traffic vào container bị lỗi kết nối DB, khác với `/health` chỉ trả 200 mà không check DB để tránh container orchestrator restart nhầm hàng loạt).

## Kết quả kiểm thử:
- Test `pytest tests/test_cp4.py -v` đã pass 100%. Mọi logic bao gồm cả timeout và connection được mô phỏng hoàn hảo.

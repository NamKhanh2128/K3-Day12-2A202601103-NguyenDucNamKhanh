# Báo cáo Checkpoint 3
**MSSV:** 2A202601103 - NguyenDucNamKhanh

## Các thay đổi đã thực hiện:
1. **`app/auth.py`**:
   - Cài đặt hàm `verify_api_key`.
   - Lấy API key từ cấu hình hệ thống bằng `get_settings().agent_api_key`.
   - So sánh bằng `secrets.compare_digest` để chống lại lỗ hổng timing attack (không dùng toán tử `==`).
   - Trả về lỗi 401 Unauthorized nếu API Key bị trống hoặc không chính xác.
   - Trả về `x_user_id` nếu người dùng truyền qua header, nếu không thì mặc định là `anonymous`.

2. **`app/rate_limiter.py`**:
   - Khởi tạo thuật toán **Sliding Window Rate Limit** thông qua Redis Sorted Set.
   - Ở mỗi cửa sổ thời gian (60s), dùng `zremrangebyscore` để xoá các yêu cầu cũ ngoài khoảng.
   - Chặn đứng yêu cầu (trả về lỗi HTTP 429 - Rate limit exceeded) nếu số lượng requests (bằng `zcard`) lớn hơn hạn mức.
   - Sử dụng `uuid4()` để đảm bảo member được tạo trong `zadd` luôn luôn duy nhất (chống mất mát request cùng timestamp).

3. **`app/cost_guard.py`**:
   - Cài đặt hệ thống bảo vệ ngân sách (Cost Guard) tích hợp Redis.
   - Lưu trữ lượng tiền tiêu dùng (spent) theo cặp user và thời gian thực.
   - Tại `check()`, ngăn chặn request tiếp tục nếu chi phí dự kiến cộng với chi phí hiện tại vượt quá ngân sách (trả về lỗi HTTP 402 - Payment Required).
   - Hàm `record()` sử dụng `incrbyfloat` để cộng dồn chi phí sau mỗi khi LLM trả về thành công.

4. **`app/main.py` (/ask endpoint)**:
   - Tích hợp 3 tầng kiểm tra, theo đúng thứ tự logic:
     1. Gọi `verify_api_key` dưới dạng Dependency Injection của FastAPI.
     2. Dùng `limiter.check(user_id)` giới hạn tần suất.
     3. Dùng `guard.check(user_id)` giới hạn lượng tiền.
   - Tương tác với LLM thông qua hàm giả lập `ask_llm`.
   - Tương tác với bộ nhớ `store.append` và `guard.record(user_id, result["cost_usd"])` sau đó log sự kiện ra màn hình bằng JSON.

## Kết quả kiểm thử:
- Đã vượt qua thành công toàn bộ `pytest tests/test_cp3.py -v`.

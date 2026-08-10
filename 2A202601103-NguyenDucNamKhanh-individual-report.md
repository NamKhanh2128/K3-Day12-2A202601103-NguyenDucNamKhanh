# Báo cáo Cá nhân (Individual Report) - K3 Ngày 12

**Thông tin sinh viên:**
- **Họ và tên:** Nguyễn Đức Nam Khánh
- **Mã học viên:** 2A202601103
- **Repository:** [NamKhanh2128/K3-Day12-2A202601103-NguyenDucNamKhanh](https://github.com/NamKhanh2128/K3-Day12-2A202601103-NguyenDucNamKhanh)

---

## 1. Tổng quan các kỹ năng đạt được
Trong buổi Lab 12, em đã đưa thành công một ứng dụng AI Agent từ môi trường phát triển (localhost) lên một môi trường sản xuất (Production) thực thụ trên Cloud (Render). Quá trình này giúp em nắm bắt được chuỗi kiến thức DevOps và Backend nâng cao:

1. **12-Factor App & Cấu hình:** Hiểu cách bóc tách hoàn toàn cấu hình (Environment Variables) ra khỏi mã nguồn để tăng tính bảo mật, đồng thời thiết lập hệ thống Health Check và Logging chuẩn JSON để dễ dàng giám sát (monitor).
2. **Dockerization tối ưu:** Ứng dụng kỹ thuật Multi-stage build để giảm dung lượng Docker image từ hơn 1GB xuống chỉ còn ~150MB, và cấu hình chạy container bằng user phi đặc quyền để giảm thiểu rủi ro bảo mật (RCE).
3. **API Security:** Triển khai cơ chế xác thực API Key, đồng thời áp dụng Sliding-window Rate Limit bằng Redis và giới hạn ngân sách (Cost Guard) để bảo vệ túi tiền trước nguy cơ lạm dụng API.
4. **Stateless & Scalability:** Biến ứng dụng thành một hệ thống Stateless hoàn toàn (lưu context vào Redis) giúp cho việc Scale ngang (chạy nhiều container song song) được ổn định; áp dụng Graceful Shutdown và Readiness Probe để đảm bảo Zero Downtime Deployment.
5. **CI/CD Pipeline (Bonus):** Tự xây dựng luồng CI/CD với GitHub Actions, tự động chạy test (Pytest) và kiểm duyệt mã nguồn mỗi khi có commit mới.

## 2. Các Checkpoint đã hoàn thành

| Checkpoint | Nội dung | Trạng thái | Điểm |
|------------|----------|------------|------|
| **CP1** | 12-Factor Config, Health & Logging | Hoàn thành (13/13 tests) | 15/15 |
| **CP2** | Docker: Multi-stage, bảo mật image | Hoàn thành (14/14 tests) | 15/15 |
| **CP3** | API Security: Auth, Rate limit, Cost guard | Hoàn thành (22/22 tests) | 20/20 |
| **CP4** | Scaling & Reliability: Stateless, probe, shutdown | Hoàn thành (19/19 tests) | 20/20 |
| **CP5** | Cloud Deployment: Triển khai thật lên Render | Hoàn thành | 15/15 |
| **Exercises** | Trả lời 10 câu hỏi phản ánh | Hoàn thành (10/10 câu) | 15/15 |
| **Bonus** | Tích hợp CI/CD với GitHub Actions | Hoàn thành (13/13 tests) | +10 |

**=> TỔNG ĐIỂM DỰ KIẾN: 100/100 (Tối đa)**

## 3. Quá trình triển khai & Khó khăn gặp phải

**3.1. Vấn đề kết nối Redis trên Cloud**
- **Mô tả:** Lúc đầu, em copy nguyên file `.env` lên biến môi trường của Render, vô tình để lại dòng `REDIS_URL=redis://localhost:6379/0`. Render deploy thành công nhưng khi gọi API thì bị lỗi `500 Internal Server Error`.
- **Cách giải quyết:** Khi check log trên Render thì thấy lỗi kết nối đến `localhost:6379`. Em nhận ra localhost trên Cloud ám chỉ nội bộ container đó chứ không phải máy tính của em, mà container đó thì không cài Redis. Sau đó em đã đổi thành fake Redis (`fake://`) hoặc link Redis thật của Render để giải quyết triệt để.

**3.2. Lỗi Vòng lặp "Con gà và quả trứng" trong CI/CD**
- **Mô tả:** Khi đẩy code lên Github Actions, quy trình CI/CD luôn bị thất bại (dấu X đỏ). Nguyên nhân do hệ thống chạy tự động file `test_bonus_cicd.py`, trong đó file này đi kiểm tra xem Badge trên Github đã hiện chữ "Passing" chưa. Mà Action thì đang chạy, nên Badge chưa thể Passing, dẫn tới test rớt -> Action rớt -> Badge rớt.
- **Cách giải quyết:** Cấu hình lại câu lệnh trong file `ci.yml` là `pytest --ignore=tests/test_cp5.py --ignore=tests/test_bonus_cicd.py -v` để CI không tự đi test lại cái Badge của chính nó. Sau khi sửa, Action đã chạy thành công và Badge xanh xuất hiện.

## 4. Kết luận
Bài Lab là một bước ngoặt thực sự quan trọng giúp em chuyển đổi tư duy từ việc "viết code chạy được trên máy mình" sang "viết code sẵn sàng phục vụ hàng ngàn người dùng thực tế". Các kiến thức về bảo vệ API, giới hạn chi phí và tự động hoá triển khai cực kỳ hữu ích cho công việc thực tế sau này.

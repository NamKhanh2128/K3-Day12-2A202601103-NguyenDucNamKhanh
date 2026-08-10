# Phiếu Phản Ánh — K3 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Nguyen Duc Nam Khanh  Mã học viên: 2A202601103

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Việc "chết sớm" cứu hệ thống ở chỗ: Nếu để mặc định là `"changeme"` và khi đưa lên production ta quên thiết lập biến môi trường, server vẫn chạy bình thường. Bất cứ ai biết mã nguồn (hoặc mò ra từ docs) cũng có thể dùng key `"changeme"` để gọi API, dẫn đến việc ta bị thất thoát tiền trả cho LLM. "Fail fast" giúp phát hiện ra lỗi cấu hình ngay lập tức lúc khởi động.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Dòng log: `{"event": "ask_completed", "level": "info", "timestamp": "2026-08-10T03:04:15.885884+00:00", "user_id": "sv-test", "tokens_in": 4, "tokens_out": 36, "cost_usd": 2.22e-05}`
> Hai việc làm được: 
> 1. Dùng các công cụ tổng hợp log (Elasticsearch, Datadog, jq) để dễ dàng filter theo `user_id` xem người dùng này đã dùng bao nhiêu tiền.
> 2. Có thể dễ dàng parse và lập biểu đồ, thiết lập alert nếu giá trị `cost_usd` tăng đột biến mà không cần phải dùng Regex phức tạp trên raw text.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ~1.1 GB |
| Multi-stage | ~150 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Chênh lệch đó là do ở phiên bản 1 stage, image chứa toàn bộ môi trường gốc (base image lớn), các công cụ build (gcc, curl, build-essential), và cả cache của apt, pip. Với Multi-stage build, ở stage cuối ta chỉ copy đúng `.venv` (môi trường đã cài package sẵn) và thư mục code cần thiết vào một base image mỏng nhẹ (như `python:3.11-slim`), vứt bỏ hoàn toàn các layer trung gian tốn kém kia.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi sửa `app/main.py` (nằm ở sau bước pip install trong Dockerfile), các layer từ `COPY requirements.txt` và `RUN pip install` được dùng lại từ cache. Các layer từ `COPY . .` trở về sau sẽ phải chạy lại.
> Nếu đặt `COPY . .` lên trước `RUN pip install`, thì chỉ cần một sự thay đổi nhỏ trong bất kỳ file code nào, layer `COPY . .` sẽ bị thay đổi hash dẫn tới làm mất cache của tất cả các layer đứng sau nó. Nghĩa là Docker sẽ chạy lại `pip install` mọi lúc build, rất mất thời gian.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Kẻ tấn công lợi dụng lỗ hổng RCE (Remote Code Execution) trong app Python. Vì app chạy bằng quyền root, attacker thao túng toàn bộ file hệ thống bên trong container. Do root trong container (nếu không được cách ly cẩn thận) cũng mang quyền năng tương đương với root trên máy host, họ có thể mount `/` của host và ghi đè file cấu hình hệ thống, từ đó chiếm hoàn toàn máy host. Lệnh `USER agent` chạy ứng dụng dưới quyền một user không có đặc quyền, do vậy ngay cả khi app bị exploit, attacker cũng chỉ kẹt ở user `agent` không có quyền thực thi thay đổi hay mount gì nguy hiểm.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Có thể gửi tối đa 20 request trong 2 giây liên tiếp. Người dùng có thể gửi 10 request vào lúc 10:00:59, chưa bị chặn. Sang đúng 10:01:00, bộ đếm bị reset về 0, họ gửi tiếp 10 request vào lúc 10:01:01. Tổng cộng 20 request trong khoảng 2 giây.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn TẦN SUẤT (số lượng request theo thời gian), còn cost guard giới hạn NGÂN SÁCH (tổng số tiền chi tiêu).
> - Rate limit cho qua nhưng cost guard chặn: Người dùng mới gửi 1 request trong phút này (chưa chạm giới hạn 10 req/phút), nhưng câu hỏi đó sinh ra 10,000 tokens output, tiền vượt quá budget của họ trong tháng. Cost guard chặn.
> - Rate limit chặn nhưng cost guard cho qua: Người dùng gửi liên tiếp 20 request cực ngắn (hỏi: 'hi'), tổng tiền vài xu (chưa hết budget), nhưng tần suất 20 req/min vượt rate limit 10 req/min. Rate limit chặn.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu gộp chung và health check check luôn Redis:
> 1. Redis mất kết nối 30 giây.
> 2. Liveness probe (health check) trên cả 3 container đồng loạt trả về lỗi/timeout.
> 3. Orchestrator (Docker/K8s) tưởng cả 3 container đang bị treo/chết, nên ra lệnh kill và restart cả 3 container cùng lúc.
> 4. Do restart liên tục, cả cụm dịch vụ sụp đổ hoàn toàn. Lẽ ra chỉ nên dùng readiness để rút container khỏi load balancer tạm thời chờ Redis phục hồi.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> `history_length` sẽ trồi sụt thất thường (ví dụ: 0, 1, 0, 0, 2...) do các requests được load balancer điều phối ngẫu nhiên (round-robin) tới 3 instances khác nhau. Mỗi instance giữ 1 bộ nhớ dict hoàn toàn độc lập nên context sẽ không được đồng bộ, "agent" bị mất trí nhớ liên tục.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Trong quá trình deploy lên Render, ban đầu em copy y nguyên file `.env` lên phần Environment Variables của Render, bao gồm cả dòng `REDIS_URL=redis://localhost:6379/0`. Khi đó Render báo deploy thành công nhưng khi gọi API `/ask` thì app bị văng lỗi `500 Internal Server Error`. Mở tab Logs trên Render ra xem thì thấy thông báo lỗi: `ConnectionError: Error 111 connecting to localhost:6379. Connection refused`. Nguyên nhân là do trên môi trường Cloud, "localhost" trỏ vào chính cái container của app chứ không phải máy tính của em, mà container đó lại không cài Redis. Em đã sửa bằng cách đổi biến môi trường `REDIS_URL` thành `fake://` và deploy lại thì API đã hoạt động bình thường.

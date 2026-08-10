# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Nguyen Duc Nam Khanh |
| Mã học viên | 2A202601103 |
| Repo | K3-Day12-2A202601103-NguyenDucNamKhanh |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com |
| Platform | Render |
| Ngày deploy | 10/08/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán |
| `AGENT_API_KEY` | ✅ | đặt trong dashboard, không nằm trong repo |
| `REDIS_URL` | ✅ | fake:// |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

Thay `<URL>` bằng Public URL ở trên:

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com/health

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com/ready

# 3. Không có API key — mong đợi 401
curl -i -X POST https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: day12-lab-secret-key-12345" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: day12-lab-secret-key-12345" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo
```

## Kết Quả Chạy Thật

Dán output của các lệnh trên vào đây:

```
HTTP/1.1 200 OK
Date: Mon, 10 Aug 2026 04:31:31 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
rndr-id: abadda39-08a5-4bbf
Server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
CF-RAY: a28c45789dad8ca6-HKG
alt-svc: h3=":443"; ma=86400

{"status":"ok","service":"day12-agent","version":"1.0.0"}

---
HTTP/1.1 200 OK
{"answer":"Với Deploy la gi, cách làm phổ biến trong production là đặt một lớp gateway phía trước để lo authentication, rate limiting và bảo vệ chi phí. (Mình đang nhớ 2 lượt trao đổi trước đó.)","user_id":"sv-test","history_length":2,"cost_usd":3.315e-05,"tokens":{"in":41,"out":45}}
```

## Ảnh Chụp Màn Hình

Đã cập nhật đầy đủ lên thư mục `screenshots/` theo hướng dẫn.

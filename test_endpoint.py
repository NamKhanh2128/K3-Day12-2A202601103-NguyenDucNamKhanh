import httpx
url = "https://k3-day12-2a202601103-nguyenducnamkhanh.onrender.com/ask"
headers = {
    "X-API-Key": "day12-lab-secret-key-12345",
    "X-User-Id": "sv-test"
}
data = {"question": "Deploy la gi"}

r = httpx.post(url, headers=headers, json=data)
print(f"Status: {r.status_code}")
print(r.text)

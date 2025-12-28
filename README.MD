# Dana Service - SOA (Service Oriented Architecture)

Sistem manajemen dana berbasis SOA dengan arsitektur hybrid SOAP + FastAPI, centralized authentication, event-driven Kafka, dan HTTP/1.1 vs HTTP/2 comparison.

## 🔧 Prerequisites

- **Python**: 3.10.*
- **MySQL**: 8.0+ (running, accessible at localhost:3306)
- **Kafka**: Zookeeper + Kafka broker (localhost:19092)
- **Git**: Untuk clone repository
- **Postman** (optional): Untuk manual API testing

### Check Prerequisites
```bash
# Python version
python --version

# MySQL (pastikan running)
mysql -u root -p -e "SELECT VERSION();"

# Kafka (pastikan broker jalan di localhost:19092)
telnet localhost 19092
```

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/whsasmita/Final-Exam-SOA.git
```

### 2. Install Dependencies (SOAP + FastAPI)
```bash
# Root directory (for SOAP + shared utilities)
pip install -r requirements.txt

# FastAPI directory
cd fastapi_dana_SOA
pip install -r requirements.txt
cd ..
```

### 3. Setup Database
Jalankan ini sekali untuk initialize database:
```bash
# Pastikan MySQL running
cd dana_service_SOA
python utils/setup_database.py
cd ..
```

**Output expected:**
```
✅ Database 'dana_service_db' created
✅ Tables created: users, accounts, transactions
✅ Sample data inserted (optional)
```

## 🚀 Running Services

Jalankan di terminal terpisah (gunakan **Terminal, PowerShell, atau Git Bash** sesuai OS):

### 1. SOAP Services (Internal API, ports 8001-8003)

**Terminal 1 - Account Service:**
```bash
cd dana_service_SOA/services/account_service
python server.py
```
Expected output: `Listening on http://127.0.0.1:8001`

**Terminal 2 - TopUp Service:**
```bash
cd dana_service_SOA/services/topup_service
python server.py
```
Expected output: `Listening on http://127.0.0.1:8002`

**Terminal 3 - Transaction Service:**
```bash
cd dana_service_SOA/services/transaction_service
python server.py
```
Expected output: `Listening on http://127.0.0.1:8003`

### 2. FastAPI Services

**Terminal 4 - Auth Service (port 8004):**
```bash
cd fastapi_dana_SOA
uvicorn services.auth-service.main:app --host 0.0.0.0 --port 8004 --reload
```
Expected output: `Uvicorn running on http://0.0.0.0:8004`

**Terminal 5 - Gateway Service HTTP/1.1 (port 8005):**
```bash
cd fastapi_dana_SOA
uvicorn services.gateway-service.main:app --host 0.0.0.0 --port 8005 --reload
```
Expected output: `Uvicorn running on http://0.0.0.0:8005`

**Terminal 6 - Gateway Service HTTP/2 (port 8006, requires TLS):**
```bash
cd fastapi_dana_SOA
hypercorn services.gateway-service.main:app --bind 0.0.0.0:8006 --certfile cert.pem --keyfile key.pem
```
Note: Untuk development, gunakan self-signed certificate (lihat section TLS Setup).

### 3. Kafka Event Consumer

**Terminal 7 - Event Consumer:**
```bash
cd fastapi_dana_SOA/event-consumer
python consumer.py
```
Expected output: `Kafka Consumer started, listening for events...`

### 4. CLI Application

**Terminal 8 - Dana Service CLI:**
```bash
python main.py
```
Expected output: Menu interaktif register/login.

---

## 🔐 Security: SOAP Service Binding

**Current State (Development)**: SOAP services bind ke `0.0.0.0` (accessible dari luar, kurang aman).

**To Improve Security** (recommended untuk development):
Edit file SOAP server.py di ketiga services:

```python
# File: dana_service_SOA/services/*/server.py

# ❌ Current (unsafe):
httpd = make_server('0.0.0.0', PORT, application)

# ✅ Change to (safe, localhost only):
httpd = make_server('127.0.0.1', PORT, application)
```

**Effect**:
- ✅ SOAP hanya accessible dari mesin lokal
- ✅ Gateway (localhost) tetap bisa akses
- ❌ External clients HARUS lewat Gateway (diminta JWT)

Setelah perubahan, restart SOAP services.

---

## 📝 Quick Start: Testing

### Option 1: CLI (Interactive)
```bash
python main.py
```

Menu:
- Register / Login
- Get Account Info
- TopUp Dana
- Transfer Dana
- Edit Account
- Logout

### Option 2: Postman (Manual API Testing)

**1. Login untuk dapat JWT:**
```
POST http://localhost:8004/api/v1/login
Body (JSON):
{
  "username": "damar",
  "password": "damar123"
}

Response:
{
  "access_token": "eyJ0eXAi...",
  "account_number": "1234567890"
}
```

**2. Copy `access_token`, gunakan di Gateway:**
```
GET http://localhost:8005/api/v1/account/info
Headers:
  Authorization: Bearer <access_token>

Response:
{
  "message": "Account info retrieved",
  "account_number": "1234567890",
  "balance": 100000
}
```

**3. TopUp:**
```
POST http://localhost:8005/api/v1/topup
Headers:
  Authorization: Bearer <access_token>
Body (JSON):
{
  "amount": 50000
}
```

**4. Transfer:**
```
POST http://localhost:8005/api/v1/transfer
Headers:
  Authorization: Bearer <access_token>
Body (JSON):
{
  "receiver_account_number": "1234567890",
  "amount": 20000
}
```

**5. Edit Account:**
```
PUT http://localhost:8004/api/v1/account/update
Headers:
  Authorization: Bearer <access_token>
Body (JSON):
{
  "username": "username_baru",
  "password": "password_baru"
}
```

---

## 📊 Load Testing: HTTP/1.1 vs HTTP/2

### Using Locust (Recommended)

**Terminal 1 - HTTP/1.1 Test (port 8005):**
```bash
locust -f tests/locustfile_http1.py
```

**Terminal 2 - HTTP/2 Test (port 8006):**
```bash
locust -f tests/locustfile_http2.py
```

Access web UI: http://localhost:8089

Settings:
- Number of users: 10
- Ramp up: 1 user/sec
- Click START

**Metrics to observe:**
- Response time (P50, P95, P99)
- Requests/sec
- Failure rate
- HTTP/2 multiplexing advantage

### Using Benchmark Script

```bash
python benchmark_http.py
```

Compares sequential vs concurrent performance for HTTP/1.1 and HTTP/2.

---

## 🔌 TLS Setup (untuk HTTP/2)

Generate self-signed certificate untuk development:

```bash
cd fastapi_dana_SOA

# Generate cert.pem & key.pem
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"

# Verify
ls -la *.pem
```

Kemudian jalankan Hypercorn:
```bash
hypercorn services.gateway-service.main:app --bind 0.0.0.0:8006 --certfile cert.pem --keyfile key.pem
```

---

## 📡 Event-Driven Architecture

### How It Works:
1. **Client** POST topup/transfer ke Gateway
2. **Gateway** forward ke SOAP, jika sukses → publish event ke Kafka
3. **Event Consumer** subscribe topic `event-stream-trpl` → process event → log/notifikasi

### Event Schema:
```json
{
  "event_id": "f7f2df7c-...",
  "type": "TRANSFER",
  "timestamp": "2025-12-21T10:15:30Z",
  "source": "gateway-service",
  "initiator_account": "1234567890",
  "target_account": "0987654321",
  "amount": 20000,
  "correlation_id": "req-abc123",
  "version": 1
}
```

### View Consumer Logs:
Terminal 7 (event consumer) akan print setiap event yang diprocess.

---

## 🛠️ Port Allocation

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Account Service | 8001 | SOAP | Internal |
| TopUp Service | 8002 | SOAP | Internal |
| Transaction Service | 8003 | SOAP | Internal |
| Auth Service | 8004 | HTTP/1.1 | Login, Register, Edit Account |
| Gateway Service | 8005 | HTTP/1.1 | Public API (topup, transfer, info) |
| Gateway Service | 8006 | HTTP/2 (TLS) | Public API (HTTP/2 variant) |
| Kafka Broker | 19092 | TCP | Event streaming |
| Locust Web UI | 8089 | HTTP | Load test dashboard |
| MySQL | 3306 | TCP | Database |

---

## 🐛 Troubleshooting

### Service tidak bisa start?
- Pastikan port tidak dipakai service lain: `netstat -ano | grep PORT`
- Matikan port yang conflict atau gunakan port berbeda

### MySQL connection error?
```bash
# Cek MySQL running
mysql -u root -p -e "SELECT 1;"

# Check env di fastapi_dana_SOA/.env:
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=<your-password>
```

### Kafka connection error?
```bash
# Pastikan Kafka broker running di localhost:19092
telnet localhost 19092

# Cek di .env:
# KAFKA_NETWORK=localhost:19092 (bukan 127.0.0.1)
```

### JWT Token expired?
- Token valid 30 menit (konfigurasi di .env: `ACCESS_TOKEN_EXPIRE_MINUTES=30`)
- Login ulang untuk dapat token baru

### SOAP service tidak bisa connect dari Gateway?
- Pastikan SOAP server sudah jalan
- Pastikan WSDL accessible: visit `http://localhost:8001?wsdl` di browser
- Cek firewall tidak block port 8001-8003

---


Semua service harus running agar sistem bekerja optimal!
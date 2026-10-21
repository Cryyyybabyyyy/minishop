# MiniShop — Intentionally Vulnerable E-Commerce Lab

**FOR AUTHORISED UNIVERSITY SSDLC / SECURITY-TESTING USE ONLY.**

This application deliberately contains three common web vulnerabilities so that
students can practise identification, exploitation (in a safe lab) and later
remediation. **Do not expose it to the public internet.**

---

## 1. Quick Start (Ubuntu + Docker)

```bash
# 1. Extract the archive
unzip minishop.zip
cd minishop

# 2. Build and start (binds to 127.0.0.1:5000 only)
docker compose up --build -d

# 3. Open the site
#    Browser: http://127.0.0.1:5000
#    or curl:
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/
```

### Synthetic accounts

| Role     | Username | Password  |
|----------|----------|-----------|
| Customer | alice    | alice123  |
| Customer | bob      | bob123    |
| Seller   | seller   | seller123 |

---

## 2. Architecture

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Backend      | Python 3.12 + Flask 3               |
| Database     | SQLite (volume-persisted)           |
| Templates    | Jinja2                              |
| Styling      | Custom CSS (responsive)             |
| Features     | Catalogue, cart, checkout, register, profile pics, seller upload |
| Runtime      | Gunicorn inside Docker (or flask run) |
| Orchestration| Docker Compose                      |

```
minishop/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py
│   ├── models.py            # SQLite schema + seed data
│   ├── routes.py            # All routes (contains intentional vulns)
│   ├── wsgi.py
│   ├── templates/           # Jinja templates
│   └── static/
│       ├── css/style.css
│       └── uploads/         # Uploaded files (volume)
├── tests/
├── evidence/                # Vulnerability documentation
├── instance/                # SQLite DB (volume)
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 3. Lab Isolation Features

- Host port binding: **127.0.0.1:5000** only
- Container runs as non-root user (`uid=1000`)
- `cap_drop: ALL`
- `no-new-privileges: true`
- CPU / memory limits
- Separate named volumes for DB and uploads
- No privileged mode, no sensitive host mounts
- Health-check on localhost inside the container

---

## 4. Intentional Vulnerabilities

Full documentation is in `evidence/VULNERABILITIES.md`. Summary:

1. **OS Command Injection** – `/diagnostics` concatenates user input into a shell command (`shell=True`).
2. **IDOR / Broken Access Control** – `/orders/<id>` does not verify order ownership.
3. **Unrestricted File Upload** – `/seller/upload` accepts any file type with only `secure_filename`.

---

## 5. Safe Reproduction of Each Vulnerability

### 5.1 Command Injection (harmless PoC)

```bash
# Login and obtain session cookie
curl -c cookies.txt -b cookies.txt -X POST http://127.0.0.1:5000/login \
  -d "username=alice&password=alice123" -L -s -o /dev/null

# Inject a harmless command
curl -c cookies.txt -b cookies.txt -X POST http://127.0.0.1:5000/diagnostics \
  -d "product_code=PROD-1;%20id" -s | grep -A5 "Result"
```

Expected: output containing `uid=1000(appuser)` (or similar) from inside the container.

**Alternative (browser):** Login → Diagnostics → enter `PROD-1; id` → submit.

### 5.2 IDOR

```bash
# Login as Alice
curl -c cookies.txt -b cookies.txt -X POST http://127.0.0.1:5000/login \
  -d "username=alice&password=alice123" -L -s -o /dev/null

# Alice's own orders are 1 and 2. Request Bob's order (id=3)
curl -c cookies.txt -b cookies.txt http://127.0.0.1:5000/orders/3 -s | grep -E "Order #|Customer"
```

Expected: Order #3 belonging to **bob** is displayed even though the session is Alice’s.

### 5.3 Unrestricted File Upload

```bash
# Login as seller
curl -c cookies.txt -b cookies.txt -X POST http://127.0.0.1:5000/login \
  -d "username=seller&password=seller123" -L -s -o /dev/null

# Upload a harmless text file
echo "lab test file" > /tmp/test_upload.txt
curl -c cookies.txt -b cookies.txt -X POST http://127.0.0.1:5000/seller/upload \
  -F "file=@/tmp/test_upload.txt" -L -s -o /dev/null

# Confirm it appears on the dashboard
curl -c cookies.txt -b cookies.txt http://127.0.0.1:5000/seller -s | grep test_upload
```

---

## 6. Testing with Security Tools

### curl
See the reproduction commands above.

### Burp Suite Community / OWASP ZAP
1. Configure the browser or system proxy to `127.0.0.1:8080` (Burp) or ZAP’s proxy port.
2. Browse `http://127.0.0.1:5000` while authenticated.
3. For IDOR: intercept a request to `/orders/1` and change the ID to `3`.
4. For command injection: intercept the diagnostics POST and modify `product_code`.
5. For file upload: use the Repeater / Intruder with different file extensions.

### Bandit (static analysis)

```bash
# Inside the project directory (or a Python venv with bandit installed)
bandit -r app/ -f txt
```

Bandit should report issues around the `subprocess` call with `shell=True`.

### Semgrep

```bash
semgrep --config=auto app/
# or a specific rule pack:
semgrep --config "p/command-injection" app/
```

### pytest

```bash
# From the project root, with dependencies installed
pip install -r requirements.txt
pytest tests/ -v
```

---

## 7. Operational Commands

```bash
# Start
docker compose up --build -d

# View logs
docker compose logs -f minishop

# Stop
docker compose down

# Reset database and uploads (destroys lab data)
docker compose down -v
docker compose up --build -d
```

---

## 8. Running Without Docker (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.wsgi:app
export DATABASE_PATH=./instance/minishop.db
export UPLOAD_FOLDER=./app/static/uploads
mkdir -p instance app/static/uploads
python -m flask run --host=127.0.0.1 --port=5000
```

---

## 9. Code Quality Checks Performed

| Check                         | Status                                      |
|-------------------------------|---------------------------------------------|
| Python syntax (compile)       | Performed during packaging                  |
| Application factory & routes  | Consistent with templates                   |
| Database init + seed data     | Implemented (Alice, Bob, Seller + 4 orders) |
| Docker / Compose config       | Non-root, loopback bind, resource limits    |
| pytest suite                  | Basic functional tests included             |
| Bandit / Semgrep results      | **Not fabricated** – run them yourself      |
| Live exploit screenshots      | **Not fabricated** – reproduce as above     |

---

## 10. Disclaimer

This software is supplied solely for educational security testing inside an
isolated laboratory environment. The authors accept no responsibility for any
use outside that context. Always obtain proper authorisation before testing
any system.

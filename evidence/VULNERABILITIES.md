# Intentional Vulnerabilities – MiniShop Lab

**WARNING:** This application is deliberately insecure for authorised university
SSDLC / penetration-testing laboratory use only.  
**Do not deploy on a public network or the open internet.**

---

## Vulnerability 1 – OS Command Injection

| Field | Detail |
|-------|--------|
| **Location** | `app/routes.py` → function `diagnostics()` |
| **Endpoint** | `POST /diagnostics` |
| **Root cause** | User-controlled form field `product_code` is concatenated into a shell command string that is executed with `subprocess.run(..., shell=True)`. No sanitisation or argument-list separation is performed. |
| **Impact** | An authenticated user can inject additional shell commands that run inside the application process (e.g. `; id`, `| whoami`). |
| **Lab constraint** | Commands execute only in the local process / container. No reverse-shell, destructive, or host-escape functionality is present. |
| **Safe PoC** | Login as any user → Diagnostics → enter `PROD-1; id` → observe `uid=` output. |

---

## Vulnerability 2 – IDOR / Broken Access Control

| Field | Detail |
|-------|--------|
| **Location** | `app/routes.py` → function `order_detail()` |
| **Endpoint** | `GET /orders/<order_id>` |
| **Root cause** | The query selects an order by primary key only. There is **no** check that `order.user_id == session['user_id']`. |
| **Impact** | Any authenticated customer can view another customer’s order details (including products, prices and status) by changing the numeric order ID in the URL. |
| **Seed data** | Alice owns orders 1 & 2; Bob owns orders 3 & 4. New orders from purchases get sequential IDs. |
| **Safe PoC** | Login as `alice` → visit `/orders/3` (Bob’s order) → order details are displayed. |

---

## Vulnerability 3 – Unrestricted File Upload

| Field | Detail |
|-------|--------|
| **Location** | `app/routes.py` → functions `seller_upload()` **and** `profile_upload()` |
| **Endpoints** | `POST /seller/upload` and `POST /profile/upload` |
| **Root cause** | Only `werkzeug.utils.secure_filename` is applied. There is no extension whitelist, content-type validation, or magic-byte inspection. |
| **Impact** | Seller or any logged-in user can upload arbitrary files (e.g. `.php`, `.html`, `.exe`, `.sh`). Files are stored under the uploads directory and can be downloaded; they are **never executed** by the application. |
| **Lab constraint** | Uploaded content is served with controlled handlers and is not interpreted as executable web content. |
| **Safe PoC (seller)** | Login as `seller` → Upload a file named `test.txt` or `payload.php`. |
| **Safe PoC (profile)** | Login as `alice` → Profile → upload any file as profile picture. |

---

## Remediation Hints (for later assignment stages)

1. **Command injection** – Use `subprocess.run([...], shell=False)` with a fixed argument list, or avoid shell entirely. Validate input against a strict allow-list.
2. **IDOR** – Add `AND user_id = ?` (or equivalent) using the authenticated user’s ID when fetching a single order.
3. **File upload** – Restrict extensions to an allow-list (e.g. `.png`, `.jpg`, `.webp`), verify content-type / magic bytes, store outside the web root with randomised names, and serve only via controlled download handlers.

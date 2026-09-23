# SmartQ 🎓

**Intelligent Student Queue & Campus Service Management System**
*University of Fort Hare — Collaborative Capstone Project 2026*

<p align="center">
  <img src="static/images/smartq-wordmark.png" alt="SmartQ wordmark" width="420"/>
</p>
<p align="center">
  <img src="static/images/smartq-icon.png" alt="SmartQ icon" width="90"/>
</p>

SmartQ is a secure, network-based queue management platform that allows
students to join campus service queues digitally and monitor their turn in
real time, while service staff manage counters, calls, no-shows and
performance analytics from role-based dashboards.

---

## 📌 Problem Statement

Students spend long periods in physical queues (Finance, Health Clinic,
Registration, IT Support) with no visibility of position or waiting time.
Lost study time, overcrowding and frustration during peak periods.
Departments lack tools to measure waiting times, peak hours, counter
utilisation and bottlenecks.

---

## ✨ Features

### 🧑‍ Students
- Register / login with role-based accounts
- View live service cards with congestion status (Normal / Moderate / Congested)
- Join a queue and receive a unique number (e.g. `FIN-A035`)
- Live status page: current number, students ahead, ML-powered wait estimate
- **Call alerts:** rising chime + phone vibration + system notification the moment they are called
- In-app notifications (called, turn approaching, served, no-show) with 1-second polling
- "I will run late — inform staff" self-service flag
- Cancel own queue entry (hidden automatically once arrived/served)

### 🧑‍💼 Service Staff
- Department-scoped dashboard with live KPIs
- FIFO **Call Next** with multi-counter capacity guard
- Mark Arrived / Served / No-Show with automatic waiting-time capture
- Reschedule running-late students (to end, or after a chosen queue number)
- Live waiting list and active calls per counter

### 📺 Public Live Display Board
- `/board/` — login-free, projector-ready screen showing the number now
  being called per service, counter assignment and waiting counts
- Audible chime on every new call; live clock; UFH blue/gold theme

### 📈 Supervisors & Administrators
- Analytics: served counts, average wait/service times, peak hours,
  counter utilisation, no-shows and cancellations
- Full-department visibility (admin)
- Django admin for users, services, counters and audit review

### 📧 Branded Email Notifications
- HTML-branded "You are up next" emails (UFH blue/gold card + CTA button)
- **Dual-channel delivery pipeline:** Gmail SMTP (port 465) with automatic
  failover to the Brevo HTTPS transactional API (port 443) — guaranteeing
  delivery even on networks that block outbound SMTP
- Admin issue reports emailed with branded template + immutable audit entry

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.14, Django 6.1 (MVT) |
| Database | PostgreSQL (production) · SQLite (prototype) · MySQL 8 (schema-portability mirror) |
| Frontend | Django templates, Bootstrap 5, vanilla JavaScript polling client |
| Real-time | JSON status APIs polled at 1–2 s (queue, notifications, staff board, public board) |
| Email | Django SMTP (Gmail, TLS 465) + Brevo HTTPS API (443) with automatic fallback |
| ML | scikit-learn (Random Forest), joblib |
| Testing | pytest, pytest-django, pytest-cov — **25/25 passing** |
| Theme | University of Fort Hare blue `#003087` & gold `#FFB81C` |

---

## 🏗️ Architecture

```text
Devices (students / staff browsers / display board)
        │  HTTP + JSON polling (1–2 s)
        ▼
Django Application Server (MVT)
  ├─ Presentation: templates, static/, smartq.css, branded email templates
  ├─ Business:     views, queue_logic, RBAC decorators, audit signals, mailer
  └─ Data access:  Django ORM
        │  TCP 5432                     │  TCP 465 / TCP 443
        ▼                               ▼
PostgreSQL (smartq_db)          Gmail SMTP  /  Brevo HTTPS API
```

---

## 🎯 Capstone Focus-Area Mapping

| Focus Area | Implementation |
| --- | --- |
| Algorithms | FIFO ordering, queue-number generation, position/estimation, congestion detection, counter allocation, concurrency control (`atomic` + `select_for_update`) |
| Database | Normalised 8-entity schema, PostgreSQL migration, fixture data migration, ERD reverse-engineered with MySQL Workbench / DBeaver |
| Models | Queue process model, state machine, queueing metrics, rule-based vs ML predictive model (69.3 % accuracy gain) |
| Software Documentation | Requirements, architecture blueprint, ERD, algorithm specs, testing, user guides |
| Networks | Client-server tiers, REST-style JSON status APIs, polling real-time, DB over TCP, LAN/hotspot deployment, **dual-channel email over 465/443 defeating campus SMTP egress filtering**, HTTPS via reverse proxy |
| Security | Hashed passwords, CSRF, RBAC decorators, immutable audit trail with IP capture, failed-login detection, 12 h session / 30 min idle policy |
| Testing | 25 automated pytest cases covering models, queue logic, RBAC, auditing and views |

---

## 🗂️ Project Structure

```text
smartq-project/
├── manage.py
├── train_waiting_model.py          # ML training & rule-vs-ML comparison
├── ml_waiting_model.joblib         # trained model (generated by script)
├── run_demo.bat                    # one-click LAN demo server
├── venv.bat                        # one-click activated terminal
├── smartq/                         # settings, urls, middleware, mailer (email pipeline)
├── accounts/                       # auth, roles, notifications, audit
├── services/                       # departments, services, counters
├── queues/                         # queue engine, analytics, public board
│   └── management/commands/seed_demo.py
├── static/                         # UFH theme CSS + brand kit (wordmark, icon)
├── templates/                      # HTML templates
│   └── emails/                     # branded HTML email templates
└── tests/                          # pytest suite (25 tests)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.14+
- PostgreSQL 14+ (or SQLite for a quick start)
- Git

### 1. Clone & prepare environment
```bash
git clone <your-repo-url>
cd smartq-project
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the database
Edit `smartq/settings.py` → `DATABASES` (PostgreSQL block) with your
credentials. For a quick local trial you may switch to the commented
SQLite block.

### 4. Migrate & seed
```bash
python manage.py migrate
python manage.py seed_demo        # demo departments, services, counters, users
python manage.py createsuperuser  # optional admin account
python manage.py runserver
```

Seeded demo accounts (password `Capstone2026!`):

| Role | Usernames |
| --- | --- |
| Staff | `staff_finance`, `staff_clinic`, `staff_ict` |
| Students | `student1`, `student2`, `student3` |

### 5. Run
```bash
python manage.py runserver              # local only
python manage.py runserver 0.0.0.0:8000 # LAN / demo mode
```

---

## 📧 Email Notification Pipeline (Networks & Security focus)

Campus enterprise Wi-Fi was empirically found to **block outbound SMTP**
(ports 25/465/587) via egress filtering — reproduced with a raw-socket
SMTP client (`TimeoutError 10060`). SmartQ therefore implements a
dual-channel pipeline:

1. **Channel 1 — SMTP:** Gmail over TLS port 465.
2. **Channel 2 — HTTPS fallback:** Brevo transactional email API over
   port 443 (never blocked), invoked automatically when SMTP fails.

Emails are HTML-branded (UFH blue/gold) with dynamic, request-derived
links (`request.build_absolute_uri`), so buttons remain correct on any
network or future domain. Delivery failures degrade gracefully — queue
operations never break because email is unavailable.

### 🔐 Confidential Credentials Notice
This repository ships with placeholder credentials for the email pipeline.
Live demo credentials (a single-purpose Gmail App Password and a free-tier
Brevo API key) are configured locally on the demo machine only and were
**revoked immediately after submission**. They are intentionally excluded
from version control in line with secure configuration-management practice.

---

## 📡 Multi-Device Demo (LAN / Hotspot)

Campus enterprise Wi-Fi typically blocks device-to-device traffic
(client isolation, VLANs, rogue-server IDS). For reliable demos:

1. Create a personal mobile hotspot
2. Connect server PC + demo devices to it
3. `python manage.py runserver 0.0.0.0:8000` (or double-click `run_demo.bat`)
4. Open `http://<server-ip>:8000` on every device
5. Project the public board: `http://<server-ip>:8000/board/`

Windows firewall (Administrator):
```bat
netsh advfirewall firewall add rule name="SmartQ Demo" dir=in action=allow protocol=TCP localport=8000 profile=any
```

---

## 🔒 HTTPS (Optional)

TLS is terminated at a Caddy reverse proxy (app bound to localhost only):

```caddyfile
:8443 {
    tls internal
    reverse_proxy 127.0.0.1:8000
}
```

Production deployments would use publicly-trusted certificates
(e.g. Let's Encrypt) with automatic renewal.

---

## 🤖 Machine Learning Investigation

```bash
python train_waiting_model.py
```

- **Features:** students ahead, average service time, active counters, hour, weekday
- **Target:** actual waiting time (minutes)
- **Data:** 18 real historical samples + 600 simulated = 618 samples
- **Evaluation:** held-out test set, Mean Absolute Error

Example output from the final training run:

```text
Rule-based MAE : 70.46 minutes
ML model MAE   : 21.63 minutes
Result: ML improves accuracy by 69.3% - ML estimate enabled in SmartQ.
```

The trained artifact (`ml_waiting_model.joblib`) is integrated into the
live estimation pipeline with automatic rule-based fallback.

---

## 🧪 Testing & Quality Assurance

```bash
pytest
```

- **25 automated tests, 100 % passing** (~71 % coverage of core modules)
- Coverage spans: model integrity, FIFO ordering, estimation & congestion
  thresholds, RBAC enforcement, immutable audit writes, and all queue views
- Isolated test database — production data never touched

---

## 🔐 Security & Audit

- Hashed passwords (PBKDF2), session + CSRF token rotation
- RBAC enforced by decorators on every staff endpoint
- Immutable audit trail (logins, failed logins, queue actions) with IP capture
- Failed-login signal monitoring for suspicious-activity detection
- Session policy: 12 h cookie lifetime, 30 min idle redirect
- Developer console: timestamped, colour-coded request log (green auth
  events, red errors) with live-polling noise filtered out

---

## 🎨 Brand Kit

| Asset | File | Usage |
| --- | --- | --- |
| Wordmark | `static/images/smartq-wordmark.png` | README, report covers, slides |
| Monogram icon | `static/images/smartq-icon.png` | Favicon, navbar, board header, login hero |
| UFH crest | `static/images/ufh-logo.png` | Navbar (paired with SmartQ icon) |

---

## 🧪 Demo Script

1. `seed_demo` → log in as `student1` on a phone (hotspot)
2. Student joins **Fee Enquiry** → receives `FIN-A001`
3. Project `/board/` on the big screen
4. Staff clicks **Call Next** → board chimes, student phone vibrates + chimes + email arrives
5. Staff marks **Arrived → Served** → analytics & audit update instantly
6. Admin reviews the immutable audit trail in `/admin/`

---

## 🛣️ Roadmap

- [ ] QR code check-in at service points
- [ ] WebSocket push updates (Django Channels)
- [ ] SMS notifications
- [ ] Demand forecasting & bottleneck detection
- [ ] Priority management with audit overrides
- [ ] Production domain + publicly-trusted TLS certificate
- [x] ~~Email notifications~~ (shipped: dual-channel SMTP/HTTPS pipeline)
- [x] ~~Public display board~~ (shipped: `/board/`)

*Note: A React SPA prototype (session-authenticated REST API + CORS) was
developed and evaluated during the project. Following comparative
evaluation, the team standardised on the Django MVT template architecture
for deployment simplicity and server-side security control; selected
innovations from the prototype (public board, audible alerts) were ported
into the template layer. The prototype is retained in the project archive
as documented future work.*

---

## 👥 Team & Role Descriptions

| # | Member | Role |
| --- | --- | --- |
| 1 | Gareth Zuma | Group Leader (GL) |
| 2 | Monwabisi Thebe | Assignment Group Leader (Assignment GL) |
| 3 | Nelisiwe Kolweni | Project Group Leader (Project GL) |
| 4 | Entle Kolisa | Presentation Group Leader (Presentation GL) |
| 5 | Luzuko Ntozonke | Research Coordinator |
| 6 | Thokozani Nyingizwayo | Documentation Coordinator |
| 7 | Amanda Nzama | System Design Coordinator |
| 8 | Lonwabo Mbhele | Developer Coordinator |
| 9 | Siphumelele Mangwane | Slide Design Coordinator |
| 10 | Rotshidzwa Tshirundu | Presentation Coordinator |
| 11 | Masimbonge Melani | Testing & QA Coordinator |
| 12 | Loyiso Skebhe | Communication & Scheduling Coordinator |
| 13 | Banele Mbokane | Repository & Version Control Coordinator |
| 14 | Inam Zitumane | Report Editor |
| 15 | Thokozani Myendeki | Support & Logistics Coordinator |

---

## 📄 License

Academic use — University of Fort Hare Capstone Project 2026.

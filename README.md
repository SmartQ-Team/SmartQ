# SmartQ 🎓

**Intelligent Student Queue & Campus Service Management System**
*University of Fort Hare — Collaborative Capstone Project 2026*

<p align="center">
  <img src="static/images/logo.png" alt="SmartQ logo" width="160"/>
</p>

SmartQ is a secure, network-based queue management platform that allows
students to join campus service queues digitally and monitor their turn in
real time, while service staff manage counters, calls, no-shows and
performance analytics from role-based dashboards.

---

## 📌 Problem Statement

- Students spend long periods in physical queues (Finance, Health Clinic,
  Registration, IT Support) with no visibility of position or waiting time.
- Lost study time, overcrowding and frustration during peak periods.
- Departments lack tools to measure waiting times, peak hours, counter
  utilisation and bottlenecks.

## ✨ Features

### 🧑‍ Students
- Register / login with role-based accounts
- View live service cards with congestion status (Normal / Moderate / Congested)
- Join a queue and receive a unique number (e.g. `FIN-A035`)
- Live status page: current number, students ahead, ML-powered wait estimate
- In-app notifications (called, turn approaching, served, no-show)
- Cancel own queue entry

### 🧑‍💼 Service Staff
- Department-scoped dashboard with KPIs
- FIFO **Call Next** with multi-counter capacity guard
- Mark **Arrived / Served / No-Show**
- Live waiting list and active calls per counter

### 📈 Supervisors & Administrators
- Analytics: served counts, average wait/service times, peak hours,
  counter utilisation, no-shows and cancellations
- Full-department visibility (admin)
- Django admin for users, services, counters and audit review

## 🧠 Waiting-Time Intelligence

- **Rule-based estimator:** `(students ahead × avg service time) ÷ active counters`
- **ML investigation:** Random Forest regression trained on historical +
  simulated queue data; automatically used when available with rule-based
  fallback (see [Machine Learning](#-machine-learning-investigation))

## 🛠️ Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python 3.14, Django 6.1 (MVT) |
| Database   | PostgreSQL (production) · SQLite (prototype) · MySQL 8 (schema-portability mirror) |
| Frontend   | Django templates, Bootstrap 5, vanilla JavaScript polling client |
| ML         | scikit-learn (Random Forest), joblib |
| Theme      | University of Fort Hare blue `#003087` & gold `#FFB81C` |

## 🏗️ Architecture

```text
Devices (students/staff browsers)
        │  HTTP(S) + JSON polling (5 s)
        ▼
Django Application Server (MVT)
  ├─ Presentation: templates, static/, smartq.css
  ├─ Business:     views, queue_logic, RBAC decorators, audit signals
  └─ Data access:  Django ORM
        │  TCP 5432
        ▼
PostgreSQL (smartq_db)
```

## 🎯 Capstone Focus-Area Mapping

| Focus Area | Implementation |
|---|---|
| Algorithms | FIFO ordering, queue-number generation, position/estimation, congestion detection, counter allocation, concurrency control (`atomic` + `select_for_update`) |
| Database | Normalised 8-entity schema, PostgreSQL migration, fixture data migration, ERD reverse-engineered with MySQL Workbench / DBeaver |
| Models | Queue process model, state machine, queueing metrics, rule-based vs ML predictive model |
| Software Documentation | Requirements, architecture blueprint, ERD, algorithm specs, testing, user guides |
| Networks | Client-server tiers, REST-style JSON status API, polling real-time, DB over TCP, LAN/hotspot deployment, HTTPS via reverse proxy |
| Security | Hashed passwords, CSRF, RBAC decorators, immutable audit trail with IP capture, failed-login detection |

## 🗂️ Project Structure

```text
smartq-project/
├── manage.py
├── train_waiting_model.py        # ML training & comparison script
├── run_demo.bat                  # one-click LAN demo server
├── venv.bat                      # one-click activated terminal
├── smartq/                       # project config (settings, urls)
├── accounts/                     # auth, roles, notifications, audit
├── services/                     # departments, services, counters
├── queues/                       # queue engine, analytics, status API
├── static/                       # UFH theme CSS + logo
├──screenshots/                   # System screenshots
└── templates/                    # all HTML templates
```

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
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Log into `/admin/` and create: **Departments → Services → Counters →
Staff profiles (roles & department)**.

### 5. Run
```bash
python manage.py runserver            # local only
python manage.py runserver 0.0.0.0:8000   # LAN / demo mode
```

## 🗄️ Database Notes

- **Production:** PostgreSQL (`smartq_db`, owned by dedicated `smartq_user`)
- **Prototype:** SQLite (`db.sqlite3`) — kept as rollback backup
- **Data migration:** performed with `dumpdata` / `loaddata` fixtures
- **Schema portability:** schema mirrored into MySQL 8 and reverse-engineered
  with Oracle MySQL Workbench (see `docs/` for ER diagrams)

## 📡 Multi-Device Demo (LAN / Hotspot)

Campus enterprise Wi-Fi typically blocks device-to-device traffic
(client isolation, VLANs, rogue-server IDS). For reliable demos:

1. Create a personal mobile hotspot
2. Connect server PC + demo devices to it
3. `python manage.py runserver 0.0.0.0:8000` (or double-click `run_demo.bat`)
4. Open `http://<server-ip>:8000` on every device

Windows firewall (Administrator):
```bat
netsh advfirewall firewall add rule name="SmartQ Demo" dir=in action=allow protocol=TCP localport=8000 profile=any
```

## 🔒 HTTPS (Optional)

TLS is terminated at a Caddy reverse proxy (app bound to localhost only):

```text
:8443 {
    tls internal
    reverse_proxy 127.0.0.1:8000
}
```

Production deployments would use publicly-trusted certificates
(e.g. Let's Encrypt) with automatic renewal.

## 🤖 Machine Learning Investigation

```bash
python train_waiting_model.py
```

- Features: students ahead, average service time, active counters, hour, weekday
- Target: actual waiting time (minutes)
- Evaluation: held-out test set, Mean Absolute Error
- Outcome: ML model saved to `ml_waiting_model.joblib` and integrated into
  the live estimation pipeline with automatic rule-based fallback

Example output:
```text
Rule-based MAE : 7.12 minutes
ML model MAE   : 2.45 minutes
Result: ML improves accuracy by 65.5% - ML estimate enabled in SmartQ.
```

## 🔐 Security & Audit

- Hashed passwords (PBKDF2), session + CSRF token rotation
- RBAC enforced by decorators on every staff endpoint
- Immutable audit trail (logins, failed logins, queue actions) with IP capture
- Failed-login signal monitoring for suspicious-activity detection

## 🧪 Demo Script

1. Window 1: student joins *Fee Enquiry* queue
2. Window 2: staff clicks **Call Next** — student page updates live
3. Student sees "called" banner + notification bell alert
4. Staff marks **Served** — analytics & audit log update instantly
5. Admin reviews the immutable audit trail

## 🛣️ Roadmap

- [ ] QR code check-in at service points
- [ ] WebSocket push updates (Django Channels)
- [ ] SMS / email notifications
- [ ] Demand forecasting & bottleneck detection
- [ ] Priority management with audit overrides

## 👥 Team & Role Descriptions

| # | Member | Role |
|---|--------|------|
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

## 📄 License

Academic use — University of Fort Hare Capstone Project 2026.

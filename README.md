# TicketMe — Event Ticketing & Management System

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**TicketMe** is a web-based Event Ticketing & Booking Management System built for event organizers, ticketing officers, and attendees in Ghana. It handles the complete lifecycle of event creation, ticket type tiering, attendee booking, payment recording, QR code generation, and ticket verification.

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **User & Role Access** | Role-based authentication (`Administrator`, `Manager`, `Ticket Officer`). |
| **Event Management** | Create and manage upcoming, ongoing, and completed events with schedule details. |
| **Multi-Tier Ticket Types** | Define VIP, Regular, Student, and Early Bird ticket tiers with custom pricing in Ghana Cedi (`GH₵`). |
| **Bookings & Payments** | Record ticket bookings and payment channels (Cash, MTN Mobile Money, Telecel Cash, Card). |
| **QR Code Verification** | Auto-generate unique QR codes per ticket for instant gate verification. |
| **Reports & Sales Dashboard** | Visual dashboards tracking revenue by event, ticket sales volume, and payment method statistics. |

---

## 🏗️ Tech Stack

- **Backend Framework:** Python Flask (Modular Blueprint Architecture)
- **Database:** MySQL / MariaDB via SQLAlchemy ORM (PyMySQL driver)
- **Authentication:** Flask-Login with password hashing (`werkzeug.security`)
- **Utilities:** `qrcode` & `Pillow` for QR code rendering, `reportlab` for PDF ticket downloads
- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Chart.js

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server (version 8.0 or MariaDB equivalent)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kingenious0/ticketme.git
   cd ticketme
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=ticketme-super-secret-key
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:1234@localhost:3306/ticketme_db
   ```

5. **Seed Database:**
   ```bash
   python seed.py
   ```

6. **Run the Application:**
   ```bash
   python run.py
   ```
   Open your browser at `http://127.0.0.1:5000`.

---

## 🔑 Demo Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Manager | `manager@ticketme.com` | `manager123` |
| Ticket Officer | `officer@ticketme.com` | `officer123` |

---

## 📄 License

This project is open-source under the MIT License.

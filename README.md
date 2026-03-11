<div align="center">

# ⚡ ElectroShop

**A modern full-featured e-commerce store for electronics, built with Django**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)](https://getbootstrap.com)

[Features](#-features) · [Quick Start](#-quick-start) · [Project Structure](#-project-structure) · [Data Models](#-data-models)

</div>

---

## ✨ Features

| Module | What it does |
|--------|-------------|
| 🛍️ **Catalog** | Browse products with filtering by category, price range, and keyword search |
| 📦 **Product Pages** | Detailed product view with related items and discount badges |
| 🛒 **Cart** | Session-based cart — works without an account |
| 📋 **Orders** | Checkout flow, order history, and per-order detail pages |
| 👤 **Accounts** | Registration, login, and editable user profile with avatar |
| 🔧 **Admin Panel** | Full Django admin for managing products, categories, and orders |

---

## 🚀 Quick Start

### 1. Clone the repository and install dependencies

```bash
git clone https://github.com/your-username/electroshop.git
cd electroshop
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_ENGINE=django.db.backends.postgresql
DB_NAME=electronics_shop
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Create the PostgreSQL database

```sql
CREATE DATABASE electronics_shop;
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load sample data *(optional)*

```bash
python manage.py loaddata fixtures/products.json
```

> Loads 15 products across 5 categories: Smartphones, Laptops, Headphones, Tablets, Accessories.

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Storefront |
| http://127.0.0.1:8000/admin | Admin panel |

---

## 📁 Project Structure

```
electroshop/
│
├── 📂 myproject/               # Project config
│   ├── settings.py             # Settings (env-based)
│   ├── urls.py                 # Root URL config
│   └── wsgi.py
│
├── 📂 store/                   # Product catalog app
│   ├── models.py               # Category, Product
│   ├── views.py                # List & detail views
│   ├── urls.py
│   └── admin.py
│
├── 📂 cart/                    # Shopping cart app
│   ├── cart.py                 # Cart logic (session-based)
│   ├── views.py
│   ├── forms.py
│   └── context_processors.py  # Injects cart into every template
│
├── 📂 orders/                  # Order management app
│   ├── models.py               # Order, OrderItem
│   ├── views.py                # Checkout, history, detail
│   ├── forms.py
│   └── admin.py
│
├── 📂 accounts/                # User accounts app
│   ├── models.py               # Profile (extends User)
│   ├── views.py                # Register, profile edit
│   └── forms.py
│
├── 📂 templates/               # Django HTML templates
│   ├── base.html               # Base layout with navbar & footer
│   ├── store/
│   ├── cart/
│   ├── orders/
│   └── accounts/
│
├── 📂 static/
│   └── css/style.css           # Custom styles (Modern Tech theme)
│
├── 📂 fixtures/
│   └── products.json           # Sample data — 15 products
│
├── .env                        # Environment variables (not in git)
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## 🗃️ Data Models

```
Category ──< Product
                │
User ──< Order ──< OrderItem >── Product
  │
  └── Profile
```

### Order statuses

| Status | Meaning |
|--------|---------|
| `pending` | Awaiting processing |
| `processing` | Being handled |
| `shipped` | On its way |
| `delivered` | Received by customer |
| `cancelled` | Cancelled |

---

## 🎨 UI & Styling

Built with **Bootstrap 5** and a fully custom CSS layer (`static/css/style.css`):

- **Fonts:** Sora (body) + Space Mono (prices, labels, monospace accents)
- **Color palette:** Deep navy primary `#2563eb` with amber `#f59e0b` accents
- **Components:** Animated product cards, sticky filter sidebar, dark order summary panel, session cart counter badge
- **Responsive:** Mobile-friendly navbar with collapsible search

---

## 📦 Requirements

```
Django>=4.2
psycopg2-binary>=2.9
Pillow>=10.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
python-dotenv
```

---

## 🔐 Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | `False` |
| `DB_NAME` | Database name | — |
| `DB_USER` | Database user | — |
| `DB_PASSWORD` | Database password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

---

## 📄 License

This project is for educational purposes. Feel free to use it as a base for your own projects.

---

<div align="center">
ElectroShop © 2026
</div>

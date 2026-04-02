# 🐄 Dairy Farm MX

A REST API backend for managing dairy farm operations — built with Django and Django REST Framework. Designed for Kenyan smallholder dairy farmers to track cattle, monitor milk production, and run their farm with data instead of guesswork.

**Status:** Active development · Core backend complete · Frontend in progress

---

## Features

### ✅ Complete
- **Cattle Management** — register and manage individual animals with tag number, breed, gender, and activity status
- **Milk Production Tracking** — log milk yield per cow with datetime, query production trends over time
- **Farmer Auth** — JWT-based authentication, farm auto-created on registration
- **Django Admin Dashboard** — full admin interface for farm data oversight

### 🔧 In Progress
- Production reports and analytics
- Expense and inventory tracking
- Scheduling and reminders
- Mobile-friendly frontend

---

## 🏗️ Architecture

This project is a **modular monolith** — a single Django application divided into focused, loosely coupled apps, each owning its domain logic.

```
dairy_farm_mx/
├── apps/
│   ├── users/          # Custom user model, registration, JWT auth
│   ├── farms/          # Farm model, auto-created on user registration
│   ├── cattle/         # Cattle registration, CRUD endpoints
│   ├── milking/        # Milk production logs, yield tracking
│   └── frontend_web/   # Django-served HTML/JS dashboard
│       └── static/
│           ├── css/styles.css
│           └── js/main.js
├── core/
│   ├── models.py
│   └── permissions.py  # IsFarmOwner permission class
├── tests/
├── config/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

**Why a modular monolith?** For an MVP at this scale, a monolith is simpler to develop and deploy while the domain is still being understood. The module boundaries are clean enough to extract into microservices later if needed.

---

## 🛠️ Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Language   | Python 3.12                                     |
| Framework  | Django 5 + Django REST Framework                |
| Database   | PostgreSQL + psycopg2                           |
| Auth       | JWT (`djangorestframework-simplejwt`)           |
| Filtering  | `django-filter`                                 |
| Admin      | Django Admin (customized)                       |
| Frontend   | Vanilla JS, HTML, CSS (Django-served templates) |

---

## ⚙️ Running Locally

### Prerequisites
- Python 3.12+
- PostgreSQL running locally
- `pip` and `virtualenv`

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/njeriwekesa/dairy-farm-management.git
cd dairy_farm_mx
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Copy `.env.example` to `.env` and fill in your values:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=dairy_farm_mx
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

**5. Create the database**
```bash
psql -U postgres -c "CREATE DATABASE dairy_farm_mx;"
```

**6. Run migrations**
```bash
python manage.py migrate
```

**7. Create a superuser** (for admin access)
```bash
python manage.py createsuperuser
```

**8. Collect static files**
```bash
python manage.py collectstatic
```

**9. Start the development server**
```bash
python manage.py runserver
```

- App: `http://127.0.0.1:8000`
- Admin: `http://127.0.0.1:8000/admin/`

---

## 📡 API Overview

All endpoints are prefixed with `/api/`.

### Auth

| Method | Endpoint               | Description                          |
|--------|------------------------|--------------------------------------|
| POST   | `/api/users/register/` | Register a new user + farm           |
| POST   | `/api/token/`          | Obtain JWT access and refresh tokens |
| POST   | `/api/token/refresh/`  | Refresh an access token              |

### Farms

| Method       | Endpoint           | Description                    |
|--------------|--------------------|--------------------------------|
| GET/POST     | `/api/farms/`      | List or create farms           |
| GET/PATCH/DELETE | `/api/farms/{id}/` | Retrieve, edit, or delete  |

### Cattle

| Method           | Endpoint            | Description                        |
|------------------|---------------------|------------------------------------|
| GET/POST         | `/api/cattle/`      | List or create cattle              |
| GET/PATCH/DELETE | `/api/cattle/{id}/` | Retrieve, edit, or delete a record |

### Milk Production

| Method           | Endpoint             | Description                              |
|------------------|----------------------|------------------------------------------|
| GET/POST         | `/api/milk/`         | List or create milk records              |
| GET/PATCH/DELETE | `/api/milk/{id}/`    | Retrieve, edit, or delete a record       |
| GET              | `/api/milk/summary/` | Aggregated totals (respects filters)     |

### Milk filter params

| Param                | Format                  | Description                        |
|----------------------|-------------------------|------------------------------------|
| `cattle__tag_number` | string                  | Exact match on cattle tag          |
| `start_date`         | `YYYY-MM-DDTHH:MM:SS`   | Records on or after this datetime  |
| `end_date`           | `YYYY-MM-DDTHH:MM:SS`   | Records on or before this datetime |

---

## 🔐 Authentication

This API uses JWT authentication via `djangorestframework-simplejwt`.

```bash
# 1. Register
POST /api/users/register/
{ "email": "farmer@example.com", "username": "farmer", "password": "yourpassword", "farm_name": "My Farm" }

# 2. Login and get tokens
POST /api/token/
{ "email": "farmer@example.com", "password": "yourpassword" }

# 3. Use the access token on all subsequent requests
Authorization: Bearer <access_token>

# 4. Refresh when expired
POST /api/token/refresh/
{ "refresh": "<refresh_token>" }
```

> The frontend does not yet implement silent token refresh — expired tokens require a manual re-login.

---

## 🗄️ Database Schema (Core Models)

```
CustomUser
├── id, email (login field), username, role (owner | manager | staff)
└── created_at, updated_at

Farm
├── id, name, location, description, established_date
├── owner (FK → CustomUser)
└── created_at, updated_at

Cattle
├── id, tag_number, name, breed, gender, date_of_birth, is_active
├── farm (FK → Farm)
└── created_at

MilkProduction
├── id, liters, date_time
├── cattle (FK → Cattle)
└── created_at
```

---

## 💡 Design Decisions

**Modular monolith** — apps are loosely coupled with clean domain boundaries, making future extraction into microservices tractable if the need arises.

**Ownership enforced at the queryset level** — every viewset's `get_queryset()` filters by `request.user`, ensuring users can never access another farm's data even with a valid object ID. Cross-user requests return `404`, not `403`, to avoid leaking record existence.

**Atomic registration** — user and farm creation are wrapped in `@transaction.atomic` in `services.py`. If either step fails, both are rolled back. No orphaned users or farms.

**PostgreSQL in development** — SQLite is not used even locally, ensuring query behavior (especially datetime range filtering on milk records) matches production exactly.

---

## 🗺️ Roadmap

- [ ] Expense and inventory tracking
- [ ] Production analytics endpoints (yield trends, per-cow averages)
- [ ] Swagger / OpenAPI documentation
- [ ] Unit test coverage (pytest-django)
- [ ] Docker + docker-compose setup
- [ ] CI/CD pipeline (GitHub Actions)

---

## 📚 App Documentation

Each app has its own README with detailed models, endpoints, serializer notes, and ownership rules.

| App | Description |
|-----|-------------|
| [`apps/users/`](apps/users/README.md) | Custom user model, registration with atomic farm creation, JWT auth, and profile endpoint. |
| [`apps/farms/`](apps/farms/README.md) | Farm model, one-farm-per-user enforcement, CRUD endpoints, and ownership scoping. |
| [`apps/cattle/`](apps/cattle/README.md) | Cattle CRUD, query filtering, farm immutability, and multi-tenant access rules. |
| [`apps/milking/`](apps/milking/README.md) | Milk production records, datetime range filtering, and aggregated summary endpoint. |
| [`apps/frontend_web/`](apps/frontend_web/README.md) | Django-served HTML/JS dashboard — auth flow, cattle and milk management UI, and summary tabs. |

---

## 👩🏽‍💻 Author

**Njeri Wekesa** — Software Developer · Python/Django · Medic-Turned-Techie


# Dairy Farm MX

A web-based dairy farm management system for recording and tracking cattle and milk production. Built with Django REST Framework on the backend and a vanilla JS frontend.

---

## Features

- **User registration and login** — new users register with credentials and a farm name; the farm is created automatically on registration
- **JWT authentication** — token stored in localStorage, sent on every API request
- **Cattle management** — add, view, edit, and delete cattle records (tag number, breed, gender)
- **Milk production records** — add, view, edit, and delete milk records linked to specific cattle
- **Date range search** — search milk records by cattle tag and optional from/to date range
- **Production summary** — daily, weekly, and monthly milk totals displayed in a tabbed summary table

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5, Django REST Framework |
| Auth | Simple JWT (`djangorestframework-simplejwt`) |
| Database | PostgreSQL + psycopg2 |
| Filtering | `django-filter` |
| Frontend | Vanilla JS, HTML, CSS (Django-served templates) |

---

## Project Structure

```
dairy_farm_mx/
├── apps/
│   ├── users/ (Custom user model,registration, JWT auth)
│   ├── farms/ (Farm model, auto-created on user registration)
│   ├── cattle/ (Cattle model, CRUD endpoints)
│   ├── milking/ (MilkProduction model, CRUD + summary endpoint)
│   └── frontend_web/ (Django views serving 
dairy_farm_mx/)
│       └──static/
│         ├── css/styles.css
│         └── js/main.js
├── core/
│   ├── models.py
│   └── permissions.py
│
├── tests/
├── manage.py
├── config/
│   ├── settings.py
│   └── urls.py
│
├── requirements.txt
├── .env 
├── .env.example 
└── .gitignore
    
```

---

## Local Setup

### Prerequisites

- Python 3.12+
- PostgreSQL running locally
- `pip` and `virtualenv`

### Steps

**1. Clone the repository**
```bash
git clone <repo-url>
cd dairy_farm_mx
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
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

**7. Collect static files**
```bash
python manage.py collectstatic
```

**8. Start the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## API Overview

All endpoints are prefixed with `/api/`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/users/register/` | Register a new user + farm |
| POST | `/api/token/` | Obtain JWT access token |
| GET/POST | `/api/farms/` | List or create farms |
| GET/POST | `/api/cattle/` | List or create cattle |
| PATCH/DELETE | `/api/cattle/{id}/` | Edit or delete a cattle record |
| GET/POST | `/api/milk/` | List or create milk records |
| PATCH/DELETE | `/api/milk/{id}/` | Edit or delete a milk record |
| GET | `/api/milk/summary/` | Aggregated totals (supports `start_date`, `end_date` filters) |

### Milk filter params

| Param | Format | Description |
|---|---|---|
| `cattle__tag_number` | string | Filter by cattle tag |
| `start_date` | `YYYY-MM-DDTHH:MM:SS` | Records on or after this datetime |
| `end_date` | `YYYY-MM-DDTHH:MM:SS` | Records on or before this datetime |

---

## User Flow

1. Navigate to `/register/` → enter email, username, password, and farm name → redirected to dashboard
2. From the dashboard, add cattle with a tag number, breed, and gender
3. Add milk production records by selecting a cow, entering liters, and picking a date and time
4. Use the search bar to filter records by cow tag and date range
5. View the Daily / Weekly / Monthly summary tabs to track production trends
6. Edit or delete any cattle or milk record directly from the table

---

## Notes

- Each user's data is scoped to their farm — users cannot view or modify records belonging to other farms
- Cattle tag numbers are unique per farm and cannot be changed after creation
- Each milk record is unique per cattle per session datetime (enforced at the database level)

---

## App Documentation

Each app has its own README with detailed models, endpoints, and usage examples.

| App | Description |
|---|---|
| [`apps/users/`](apps/users/README.md) | User registration, JWT login/refresh, and profile retrieval. Covers the custom user model, role field, and authentication endpoints. |
| [`apps/farms/`](apps/farms/README.md) | Farm creation and management. Each farm is automatically assigned to its owner on registration. Covers the Farm model, CRUD endpoints, and ownership rules. |
| [`apps/cattle/`](apps/cattle/README.md) | Cattle CRUD with multi-tenant ownership enforcement. Covers filtering, farm immutability, and security rules for cross-user access prevention. |
| [`apps/milking/`](apps/milking/README.md) | Milk production recording, filtering by cow tag and date range, and aggregated totals via the summary endpoint. |
| [`apps/frontend_web/`](apps/frontend_web/README.md) | Django-served HTML/JS frontend. Covers the dashboard UI, static file setup, and how the frontend communicates with the REST API. |
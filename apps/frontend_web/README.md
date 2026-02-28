# Frontend Web

The `frontend_web` app is a Django app responsible for serving the HTML templates and static files that make up the browser-based UI for Dairy Farm MX. It communicates with the REST API entirely through `fetch` calls in vanilla JavaScript — there is no separate frontend framework or build step.

---

## Structure

```
apps/frontend_web/
├── templates/
│   ├── base.html           # Base layout: navbar, static file loading
│   ├── login.html          # Login form
│   ├── register.html       # Registration form
│   └── dashboard.html      # Main dashboard (cattle + milk management)
├── views.py                # Simple Django views that render each template
└── urls.py                 # URL routes for /login/, /register/, /dashboard/
static/
├── css/styles.css          # Global styles
└── js/main.js              # All frontend logic (auth, CRUD, summary tabs)
```

---

## Pages & Routes

| URL | Template | Description |
|---|---|---|
| `/login/` | `login.html` | Email + password login form |
| `/register/` | `register.html` | Registration form with farm name |
| `/dashboard/` | `dashboard.html` | Main UI for managing cattle and milk records |

---

## How It Works

Authentication is handled entirely on the client side using JWT. On login or registration, the access token is saved to `localStorage` and attached as a `Bearer` header on every subsequent API request. The navbar is rendered dynamically based on whether a token is present.

The dashboard makes the following API calls on load:

1. `GET /api/farms/` — fetches the user's farm ID, required for creating cattle
2. `GET /api/cattle/` — populates the cattle table and the cattle dropdown in the milk form
3. `GET /api/milk/` — populates the milk records table and the summary tabs

All CRUD operations (create, edit, delete) update the relevant table in place without a page reload.

---

## Dashboard Features

### Cattle
- Add cattle with tag number, breed, and gender
- Click **Edit** on any row to pre-fill the form; save sends a `PATCH` request
- Tag number is locked during edit (unique per farm, immutable after creation)
- Search by tag number filters the table client-side

### Milk Records
- Add a record by selecting a cow, entering liters, and picking a date and time
- Click **Edit** to pre-fill the form; cattle selection is locked (immutable after creation)
- Search by cow tag and optional from/to date range — filters sent as API query params
- **Daily / Weekly / Monthly** summary tabs group all loaded records client-side and display totals in a table

---

## Static Files

Static files are served by Django during development via `django.contrib.staticfiles`. Ensure `STATIC_URL` and `STATICFILES_DIRS` are configured in `settings.py`, and run:

```bash
python manage.py collectstatic
```

---

## Notes

- The frontend does not use any JS framework, bundler, or package manager
- All state (farm ID, cattle map, milk records) is held in memory for the duration of the session
- Token refresh is not yet implemented — if the access token expires, the user will need to log in again
# Milk Production Management

The Milk Production module allows farm owners to track, record, and analyze daily milk production per cow. This is part of the MVP for the dairy farm management system.

## Features (MVP)

- Record milk production per cow (liters)
- Track date and time of milking sessions
- Link production records to specific cows
- Calculate total and average production per cow
- Aggregation endpoint for total and average liters
- Filtering by cow tag number and date range

## Models

### MilkProduction

| Field      | Type             | Description                         |
|-----------|-----------------|-------------------------------------|
| cattle    | ForeignKey(Cattle) | Cow associated with this record      |
| date_time | DateTimeField     | Date and time of milking session     |
| liters    | DecimalField      | Milk produced in liters               |
| created_at| DateTimeField     | Record creation timestamp (auto)     |

## API Endpoints

| Method | URL                      | Description                                    |
|-------|--------------------------|------------------------------------------------|
| GET    | `/api/milk/`             | List milk records for logged-in user’s farm   |
| POST   | `/api/milk/`             | Create a new milk production record           |
| GET    | `/api/milk/{id}/`        | Retrieve a single record                       |
| PUT    | `/api/milk/{id}/`        | Update a record (cannot change cattle)        |
| DELETE | `/api/milk/{id}/`        | Delete a record                                |
| GET    | `/api/milk/summary/`     | Get total and average liters (respects filters) |

## Filtering

Supported query parameters for `/api/milk/`:

- `cattle__tag_number` – Filter by cow tag
- `start_date` – Filter records from this date (inclusive)
- `end_date` – Filter records up to this date (inclusive)

Example:

```http
GET /api/milk/?cattle__tag_number=COW001&start_date=2026-02-01&end_date=2026-02-28
```
## Permissions

Only authenticated users can access this module.

Users can only view, update, or delete milk records belonging to cows in their own farm(s).

## Testing

Automated tests cover:

Full CRUD operations

Aggregation endpoint

Multi-tenant access restrictions

Filtering by cow tag and date

Run tests:

```pytest tests/test_milking.py```

## Notes

MVP does not yet include production trends visualization.

Future updates may add charts, weekly/monthly summaries, and export functionality.
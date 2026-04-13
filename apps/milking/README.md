# Milking App

Records and tracks milk production per cow. Supports full CRUD, datetime range filtering, and an aggregation endpoint for totals and averages. All records are scoped to the authenticated user's farm.

---

## Model: `MilkProduction`

| Field        | Type          | Notes                                              |
|--------------|---------------|----------------------------------------------------|
| `id`         | AutoField     | Primary key                                        |
| `cattle`     | ForeignKey    | Links to `Cattle`; immutable after creation        |
| `date_time`  | DateTimeField | Date and time of the milking session (db indexed)  |
| `liters`     | DecimalField  | Max 6 digits, 2 decimal places                     |
| `created_at` | DateTimeField | Auto-set on creation                               |

> `UniqueConstraint(fields=["cattle", "date_time"])` — one record per cow per session datetime. Duplicate entries return `400`.

---

## Endpoints

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint             | Description                                         |
|--------|----------------------|-----------------------------------------------------|
| GET    | `/api/v1/milk/`         | List milk records for the user's farm               |
| POST   | `/api/v1/milk/`         | Create a new milk production record                 |
| GET    | `/api/v1/milk/{id}/`    | Retrieve a single record                            |
| PUT    | `/api/v1/milk/{id}/`    | Full update (`cattle` field is read-only)           |
| PATCH  | `/api/v1/milk/{id}/`    | Partial update — typically `liters` or `date_time`  |
| DELETE | `/api/v1/milk/{id}/`    | Delete a record                                     |
| GET    | `/api/v1/milk/summary/` | Aggregated totals and averages (respects filters)   |

---

### Create a Record
`POST /api/v1/milk/`

**Request:**
```json
{
  "cattle": 1,
  "date_time": "2026-02-27T07:00:00",
  "liters": "20.00"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "cattle": 1,
  "date_time": "2026-02-27T07:00:00Z",
  "liters": "20.00",
  "created_at": "2026-02-27T07:05:00Z"
}
```

### Summary Endpoint
`GET /api/v1/milk/summary/`

Returns flat totals only. Daily/weekly/monthly grouping is handled client-side in the frontend — the API does not group by period.

**Response `200`:**
```json
{
  "total_liters": 145.50,
  "average_liters_per_record": 18.19
}
```

---

## Filtering

`/api/v1/milk/` and `/api/v1/milk/summary/` support the following query parameters.

| Param                | Format                  | Description                              |
|----------------------|-------------------------|------------------------------------------|
| `cattle__tag_number` | string                  | Exact match on cattle tag number         |
| `start_date`         | `YYYY-MM-DDTHH:MM:SS`   | Records on or after this datetime        |
| `end_date`           | `YYYY-MM-DDTHH:MM:SS`   | Records on or before this datetime       |

> `date_time` is a `DateTimeField` — filters require a full datetime string, not a date-only string. Date-only values (`2026-02-01`) will not match correctly.

Example:
```
GET /api/v1/milk/?cattle__tag_number=COW001&start_date=2026-02-01T00:00:00&end_date=2026-02-28T23:59:59
```

---

## Permissions & Ownership

- `get_queryset()` filters by `cattle__farm__owner=request.user`
- `validate_cattle()` in the serializer checks that the cattle belongs to the requesting user's farm — prevents logging milk for another user's cow even with a valid cattle ID
- `cattle` is set to `read_only=True` on update via `get_fields()` — a record cannot be reassigned to a different cow after creation

---

## Serializer Notes

`MilkProductionSerializer` uses `fields = "__all__"`. Ownership validation in `validate_cattle()` accesses `self.context["request"].user` — this context is automatically injected by DRF when the serializer is used inside a viewset, but must be passed manually if the serializer is instantiated outside one.

---

## Notes

- Deleting a cattle record will cascade-delete all its milk production records
- The `date_time` field is indexed for query performance on date range filtering
- The `summary/` endpoint aggregates across the filtered queryset — combine it with `start_date` / `end_date` for period-specific totals
- Tests available in `tests/test_milking.py` using `pytest` and DRF's `APIClient`

---

## Development

See the [project README](../../README.md) for local setup, environment variables, and how to run the development server.
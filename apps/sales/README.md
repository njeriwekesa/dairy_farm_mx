# Sales App

Tracks milk sales by buyer. Supports buyer management, sale recording with computed totals, date and buyer filtering, and per-buyer revenue summaries. All records are scoped to the authenticated user's farm.

---

## Model: `Buyer`

| Field        | Type          | Notes                                                      |
|--------------|---------------|------------------------------------------------------------|
| `id`         | AutoField     | Primary key                                                |
| `farm`       | ForeignKey    | Links to `Farm`                                            |
| `name`       | CharField     | Buyer name; unique per farm (`unique_together`)            |
| `buyer_type` | CharField     | `walk_in` / `b2b`                                          |
| `contact`    | CharField     | Optional; blank allowed                                    |
| `notes`      | TextField     | Optional; blank allowed                                    |
| `is_active`  | BooleanField  | Defaults to `True`; use `False` for deactivation           |
| `created_at` | DateTimeField | Auto-set on creation                                       |

---

## Model: `Sale`

| Field             | Type          | Notes                                                          |
|-------------------|---------------|----------------------------------------------------------------|
| `id`              | AutoField     | Primary key                                                    |
| `farm`            | ForeignKey    | Links to `Farm`                                                |
| `buyer`           | ForeignKey    | Links to `Buyer`; `on_delete=PROTECT`                          |
| `liters_sold`     | DecimalField  | Max 6 digits, 2 decimal places                                 |
| `price_per_litre` | DecimalField  | Max 8 digits, 2 decimal places                                 |
| `total_amount`    | DecimalField  | Max 10 digits, 2 decimal places; computed in service, read-only |
| `date`            | DateField     | Sale date (db indexed)                                         |
| `notes`           | TextField     | Optional; blank allowed                                        |
| `created_at`      | DateTimeField | Auto-set on creation                                           |

---

## Endpoints

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint                | Description                                                |
|--------|-------------------------|------------------------------------------------------------|
| GET    | `/api/v1/buyers/`       | List buyers belonging to the authenticated user's farm     |
| POST   | `/api/v1/buyers/`       | Create a buyer                                             |
| GET    | `/api/v1/buyers/{id}/`  | Retrieve one buyer                                         |
| PUT    | `/api/v1/buyers/{id}/`  | Full update of buyer                                       |
| PATCH  | `/api/v1/buyers/{id}/`  | Partial update of buyer (e.g. deactivate with `is_active`) |
| DELETE | `/api/v1/buyers/{id}/`  | Always blocked at API level (`405`)                        |
| GET    | `/api/v1/sales/`        | List sales for the authenticated user's farm               |
| POST   | `/api/v1/sales/`        | Create a sale (computes `total_amount`)                    |
| GET    | `/api/v1/sales/{id}/`   | Retrieve one sale                                          |
| PUT    | `/api/v1/sales/{id}/`   | Full update of sale (`total_amount` remains read-only)     |
| PATCH  | `/api/v1/sales/{id}/`   | Partial update of sale (`total_amount` remains read-only)  |
| DELETE | `/api/v1/sales/{id}/`   | Delete a sale                                              |
| GET    | `/api/v1/sales/summary/`| Aggregate totals and per-buyer revenue (respects filters)  |

---

### Create Buyer
`POST /api/v1/buyers/`

**Request:**
```json
{
  "farm": 1,
  "name": "Fresh Milk Kiosk",
  "buyer_type": "walk_in",
  "contact": "0700000000",
  "notes": "Collects every morning",
  "is_active": true
}
```

**Response `201`:**
```json
{
  "id": 1,
  "farm": 1,
  "name": "Fresh Milk Kiosk",
  "buyer_type": "walk_in",
  "contact": "0700000000",
  "notes": "Collects every morning",
  "is_active": true,
  "created_at": "2026-04-10T08:00:00Z"
}
```

**Validation error `400` — duplicate name on same farm:**
```json
{
  "non_field_errors": ["The fields farm, name must make a unique set."]
}
```

### Delete Buyer (Blocked)
`DELETE /api/v1/buyers/{id}/`

**Response `405`:**
```json
{
  "detail": "Buyers cannot be deleted. Set is_active=False to deactivate."
}
```

### Create Sale
`POST /api/v1/sales/`

**Request:**
```json
{
  "farm": 1,
  "buyer": 1,
  "liters_sold": "10.50",
  "price_per_litre": "42.00",
  "date": "2026-04-10",
  "notes": "Morning sale"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "farm": 1,
  "buyer": 1,
  "liters_sold": "10.50",
  "price_per_litre": "42.00",
  "total_amount": "441.00",
  "date": "2026-04-10",
  "notes": "Morning sale",
  "created_at": "2026-04-10T09:00:00Z"
}
```

### Sales Summary
`GET /api/v1/sales/summary/`

Returns aggregate totals for the filtered queryset plus grouped results by buyer.

**Response `200`:**
```json
{
  "total_sales": 3,
  "total_revenue": 1020.00,
  "total_liters_sold": 23.00,
  "by_buyer": [
    {
      "buyer_id": 1,
      "buyer_name": "Fresh Milk Kiosk",
      "buyer_type": "walk_in",
      "total_liters": 15.00,
      "total_revenue": 620.00,
      "sales_count": 2
    },
    {
      "buyer_id": 2,
      "buyer_name": "Hotel Buyer",
      "buyer_type": "b2b",
      "total_liters": 8.00,
      "total_revenue": 400.00,
      "sales_count": 1
    }
  ]
}
```

---

## Filtering

`/api/v1/sales/` and `/api/v1/sales/summary/` support the following query parameters.

| Param               | Format       | Description                                  |
|---------------------|--------------|----------------------------------------------|
| `start_date`        | `YYYY-MM-DD` | Sales on or after this date                  |
| `end_date`          | `YYYY-MM-DD` | Sales on or before this date                 |
| `buyer`             | integer      | Exact buyer ID                               |
| `buyer__buyer_type` | string       | Exact buyer type (`walk_in` or `b2b`)        |

Example:
```
GET /api/v1/sales/?start_date=2026-04-01&end_date=2026-04-30&buyer__buyer_type=b2b
```

---

## Services

### `create_sale(farm, buyer, liters_sold, price_per_litre, date, notes=None)`

Located in `services.py`. Handles sale creation rules and computed fields.

- Validates `buyer.farm == farm`; raises validation error if the buyer belongs to a different farm
- Computes `total_amount = liters_sold * price_per_litre`
- Persists and returns the created `Sale` instance

### `get_sales_summary(queryset)`

Receives an already-filtered `Sale` queryset from the viewset.

- Computes overall totals: `total_sales`, `total_revenue`, `total_liters_sold`
- Groups by buyer and returns per-buyer totals and sale counts
- Returns a dictionary with top-level totals and a `by_buyer` list

---

## Permissions & Ownership

- `get_queryset()` in both viewsets scopes records to `farm__owner=request.user`
- Cross-user object access returns `404` (not `403`) due to queryset scoping
- `create_sale()` enforces cross-model ownership integrity by rejecting buyers from another farm

---

## Serializer Notes

- `SaleSerializer` marks `total_amount` as read-only; client-supplied values are ignored
- `BuyerViewSet.destroy()` always returns `405`; buyers are deactivated via `is_active=False`, not hard-deleted
- `farm` is read-only on update for both buyer and sale serializers

---

## Notes

- `Buyer` enforces `unique_together = ("farm", "name")` — duplicate buyer names are allowed across different farms, but not within the same farm
- `Sale.buyer` uses `on_delete=PROTECT`; at the DB level this prevents deleting a buyer with sales history
- In practice, the API blocks all buyer hard deletes (`405`) regardless of sales history
- `total_amount` is always computed in service logic and never set directly by API clients
- Tests available in `tests/test_sales.py` using `pytest` and DRF's `APIClient`

---

## Development

See the [project README](../../README.md) for local setup, environment variables, and how to run the development server.

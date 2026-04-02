# Cattle App

Manages cattle records for authenticated farm owners. All cattle are scoped to the authenticated user's farm — users cannot view or modify cattle belonging to other farms.

---

## Model: `Cattle`

| Field           | Type          | Notes                                              |
|-----------------|---------------|----------------------------------------------------|
| `id`            | AutoField     | Primary key                                        |
| `farm`          | ForeignKey    | Links to `Farm`; immutable after creation          |
| `tag_number`    | CharField     | Required; unique per farm                          |
| `name`          | CharField     | Optional common name (`blank=True`)                |
| `breed`         | CharField     | Required                                           |
| `gender`        | CharField     | `male` or `female`                                 |
| `date_of_birth` | DateField     | Optional (`null=True`, `blank=True`)               |
| `is_active`     | BooleanField  | Defaults to `True`                                 |
| `created_at`    | DateTimeField | Auto-set on creation                               |

> `unique_together = ("farm", "tag_number")` — the same tag number can exist across different farms but not within the same farm.

---

## Endpoints

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint            | Description                          |
|--------|---------------------|--------------------------------------|
| GET    | `/api/cattle/`      | List all cattle for the user's farm  |
| POST   | `/api/cattle/`      | Add a new cattle record              |
| GET    | `/api/cattle/{id}/` | Retrieve a single cattle record      |
| PUT    | `/api/cattle/{id}/` | Full update of a cattle record       |
| PATCH  | `/api/cattle/{id}/` | Partial update (e.g. breed, gender)  |
| DELETE | `/api/cattle/{id}/` | Delete a cattle record               |

> Requests for cattle belonging to another user's farm return `404`, not `403`, to avoid leaking record existence.

---

### Create Cattle
`POST /api/cattle/`

**Request:**
```json
{
  "farm": 1,
  "tag_number": "COW001",
  "breed": "Friesian",
  "gender": "female"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "farm": 1,
  "tag_number": "COW001",
  "name": "",
  "breed": "Friesian",
  "gender": "female",
  "date_of_birth": null,
  "is_active": true,
  "created_at": "2026-02-24T09:00:00Z"
}
```

### Update Cattle
`PATCH /api/cattle/{id}/`

`farm` is read-only on update and will be ignored if included. `tag_number` is technically patchable but should not be changed once milk records exist, as it is used as a display identifier across the system.

**Request:**
```json
{
  "breed": "Jersey",
  "gender": "female"
}
```

---

## Query Filtering

`/api/cattle/` supports the following query parameters:

| Param       | Type    | Description                                                        |
|-------------|---------|--------------------------------------------------------------------|
| `breed`     | string  | Exact match on breed                                               |
| `gender`    | string  | `male` or `female`                                                 |
| `is_active` | boolean | `true` or `false`                                                  |
| `search`    | string  | Partial match on `tag_number` or `name`                            |
| `ordering`  | string  | `date_of_birth` or `created_at` (prefix `-` for descending order) |

Example:
```
GET /api/cattle/?gender=female&is_active=true&ordering=-created_at
```

---

## Permissions & Ownership

- `IsFarmOwner` custom permission class applied at object level (defined in `core/permissions.py`)
- `get_queryset()` filters by `farm__owner=request.user`
- `perform_create()` verifies `farm.owner == request.user` before saving — prevents a user from creating cattle under a farm they don't own even with a valid farm ID

---

## Serializer Notes

`CattleSerializer` uses `fields = "__all__"`. The `farm` field is set to `read_only=True` on update via `get_fields()`, preventing reassignment of cattle to a different farm after creation.

---

## Notes

- Deleting a cattle record will cascade-delete all associated milk production records
- `is_active` supports soft-deactivation but is not filtered by default in `get_queryset()` — all cattle are returned regardless of active status unless explicitly filtered
- Tests available in `tests/test_cattle.py` using `pytest` and DRF's `APIClient`

---

## Development

See the [project README](../../README.md) for local setup, environment variables, and how to run the development server.
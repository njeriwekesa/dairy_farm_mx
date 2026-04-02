# Farms App

Manages farm records for authenticated users. Each user owns exactly one farm, which is created automatically during registration. All other apps (cattle, milking) scope their data to the farm via ownership checks.

---

## Model: `Farm`

| Field              | Type          | Notes                                              |
|--------------------|---------------|----------------------------------------------------|
| `id`               | AutoField     | Primary key                                        |
| `owner`            | ForeignKey    | Links to `CustomUser` — one farm per user enforced by serializer |
| `name`             | CharField     | Required                                           |
| `location`         | CharField     | Optional (`blank=True`)                            |
| `description`      | TextField     | Optional (`blank=True`)                            |
| `established_date` | DateField     | Optional (`null=True`, `blank=True`)               |
| `created_at`       | DateTimeField | Auto-set on creation                               |
| `updated_at`       | DateTimeField | Auto-updated on save                               |

> `owner` is a `ForeignKey` in the model (not `OneToOneField`), but `FarmSerializer.validate()` enforces one farm per user at the serializer level, rejecting a second farm with a `400`.

---

## Endpoints

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint           | Description                        |
|--------|--------------------|------------------------------------|
| GET    | `/api/farms/`      | List the authenticated user's farm |
| POST   | `/api/farms/`      | Create a new farm                  |
| GET    | `/api/farms/{id}/` | Retrieve farm details              |
| PUT    | `/api/farms/{id}/` | Full update of farm details        |
| PATCH  | `/api/farms/{id}/` | Partial update of farm details     |
| DELETE | `/api/farms/{id}/` | Delete the farm                    |

> `get_queryset()` filters by `owner=request.user` — requests for another user's farm return `404`.

---

### Create a Farm
`POST /api/farms/`

> In normal usage this is called automatically during registration via `register_farm_owner()` in `apps/users/services.py`. Direct POST is available but rejected if the user already has a farm.

**Request:**
```json
{
  "name": "Green Valley Dairy",
  "location": "Nakuru County",
  "description": "A small family-owned dairy farm",
  "established_date": "2020-05-15"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "name": "Green Valley Dairy",
  "location": "Nakuru County",
  "description": "A small family-owned dairy farm",
  "established_date": "2020-05-15",
  "created_at": "2026-02-24T08:57:41Z",
  "updated_at": "2026-02-24T08:57:41Z"
}
```

**Error `400` — second farm attempt:**
```json
{
  "non_field_errors": ["You already have a registered farm."]
}
```

---

## Serializer Notes

`FarmSerializer` excludes `owner` from its `fields` list — it is never exposed or accepted in API requests. Ownership is assigned by `FarmViewSet.perform_create()` via `serializer.save(owner=self.request.user)`.

`FarmSerializer.create()` does not pass `owner` directly — do not call it outside of the viewset context.

---

## Notes

- The one-farm restriction is intentional for the MVP; future versions may allow multiple farms per user
- Deleting a farm will cascade-delete all cattle and milk records linked to it
- Tests available in `tests/test_farms.py` using `pytest` and DRF's `APIClient`

---

## Development

See the [project README](../../README.md) for local setup, environment variables, and how to run the development server.
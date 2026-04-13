# Users App

Handles user registration, JWT authentication, and profile retrieval. Uses a custom user model (`CustomUser`) that authenticates via email instead of username.

---

## Model: `CustomUser`

Extends Django's `AbstractUser`.

| Field        | Type          | Notes                                                        |
|--------------|---------------|--------------------------------------------------------------|
| `email`      | EmailField    | Unique — used as the login identifier (`USERNAME_FIELD`)     |
| `username`   | CharField     | Required, inherited from `AbstractUser`                      |
| `role`       | CharField     | `owner` / `manager` / `staff` — defaults to `owner`         |
| `created_at` | DateTimeField | Auto-set on creation                                         |
| `updated_at` | DateTimeField | Auto-updated on save                                         |

> The `role` field exists for future permission expansion and is not currently enforced in any view logic.

---

## Endpoints

### Register
`POST /api/v1/users/register/`

Creates a new user and automatically creates an associated farm in a single atomic transaction via `register_farm_owner()` in `services.py`.

**Request:**
```json
{
  "email": "farmer@example.com",
  "username": "farmer",
  "password": "StrongPass123",
  "farm_name": "My Dairy Farm"
}
```

**Response `201`:**
```json
{
  "message": "Farm owner registered successfully"
}
```

**Validation error `400` — duplicate credentials:**
```json
{
  "email": ["A user with that email already exists."],
  "username": ["A user with that username already exists."]
}
```

---

### Login
`POST /api/v1/token/`

**Request:**
```json
{
  "email": "farmer@example.com",
  "password": "StrongPass123"
}
```

**Response `200`:**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

### Refresh Token
`POST /api/v1/token/refresh/`

**Request:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response `200`:**
```json
{
  "access": "<new_access_token>"
}
```

---

### Get Own Profile
`GET /api/v1/users/me/`

Requires `Authorization: Bearer <access_token>`.

**Response `200`:**
```json
{
  "id": 1,
  "email": "farmer@example.com",
  "username": "farmer",
  "role": "owner",
  "farms": [
    {
      "id": 1,
      "name": "My Dairy Farm",
      "location": "",
      "description": "",
      "established_date": null,
      "created_at": "2026-02-22T05:00:00Z",
      "updated_at": "2026-02-22T05:00:00Z"
    }
  ],
  "created_at": "2026-02-22T05:00:00Z"
}
```

> `farms` is a nested array (not a flat `farm_name` string) — serialized by `FarmSerializer` via `SerializerMethodField`.

---

## Service: `register_farm_owner`

Located in `services.py`. Wraps user and farm creation in `@transaction.atomic` — if either step fails, both are rolled back.

```python
@transaction.atomic
def register_farm_owner(validated_data):
    user = CustomUser.objects.create_user(...)
    farm = Farm.objects.create(name=validated_data["farm_name"], owner=user)
    return user
```

---

## Serializer Notes

`RegisterSerializer` validates uniqueness of `email` and `username` before hitting the database, returning a clean `400` on conflict. Calls `register_farm_owner` on save.

`UserProfileSerializer` is read-only. The `farms` field uses `SerializerMethodField` and supports both `ForeignKey` (`farms`) and `OneToOne` (`farm`) relationships via a `hasattr` check.

---

## Notes

- All registered users default to the `owner` role — no public signup for other roles
- Token refresh is provided by `simplejwt` but the frontend does not implement silent refresh; expired tokens require a manual re-login
- Tests available in `tests/test_users.py` using `pytest` and DRF's `APIClient`

---

## Development

See the [project README](../../README.md) for local setup, environment variables, and how to run the development server.
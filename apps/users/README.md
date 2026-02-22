# Authentication & User Profile Feature

## Overview
This module provides:
- **User registration** (farm owner signup)
- **JWT authentication** (login, refresh token)
- **Profile retrieval** (view own user details)

---

## Endpoints

### 1. Register
**URL:** /api/users/register/

**Method:** POST 

**Payload:**
```json
{
  "email": "farmer@example.com",
  "username": "farmer",
  "password": "StrongPass123",
  "farm_name": "My Dairy Farm"
}
Response (201 Created):

{
  "message": "Farm owner registered successfully"
}
```

2. Login (JWT)

URL: /api/token/

Method: POST

Payload:

```json
{
  "email": "farmer@example.com",
  "password": "StrongPass123"
}
Response:

{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

3. Refresh Token

URL: /api/token/refresh/

Method: POST

Payload:

```json
{
  "refresh": "<refresh_token>"
}
Response:

{
  "access": "<new_access_token>"
}
```
4. Get Own Profile

URL: /api/users/me/

Method: GET

Headers:

```json
Authorization: Bearer <access_token>
Response:

{
  "id": 1,
  "email": "farmer@example.com",
  "username": "farmer",
  "role": "owner",
  "farm_name": "My Dairy Farm",
  "created_at": "2026-02-22T05:00:00Z"
}
```
*Notes*

The role field exists for future expansion (e.g., manager, staff).

Only registered users can obtain JWT tokens and access the profile endpoint.

All endpoints expect JSON requests and return JSON responses.

*Testing*

Manual tests performed using curl commands.

Automated tests available in tests/test_users.py using pytest and APIClient.


# Farm Management Feature

## Overview
This module handles farm management for the Dairy Farm system. Each user can currently own **one farm**, and the farm is automatically assigned to the user upon creation.

## Models

### `Farm`
| Field             | Type                 | Notes                                      |
|------------------|--------------------|--------------------------------------------|
| `name`           | CharField           | Name of the farm (required)               |
| `location`       | CharField           | Farm location (required)                  |
| `description`    | TextField           | Optional description of the farm          |
| `established_date` | DateField         | Optional date farm was established       |
| `owner`          | OneToOneField (User)| Automatically assigned upon creation      |
| `created_at`     | DateTimeField       | Auto-generated timestamp                  |
| `updated_at`     | DateTimeField       | Auto-generated timestamp                  |

---

## API Endpoints

All endpoints require **authentication**.

| Endpoint                | Method | Description                              |
|-------------------------|--------|------------------------------------------|
| `/api/farms/`           | GET    | Retrieve the logged-in user's farm       |
| `/api/farms/`           | POST   | Create a new farm (assigned to user)     |
| `/api/farms/{id}/`      | GET    | Retrieve farm details                     |
| `/api/farms/{id}/`      | PUT    | Update farm details                       |
| `/api/farms/{id}/`      | PATCH  | Partial update of farm details            |
| `/api/farms/{id}/`      | DELETE | Delete the farm                           |

> Note: Users can only access their own farm(s) at this stage.

---

## Behavior & Rules
- **One farm per user**: Attempting to create a second farm will return an error.  
- **Ownership assignment**: The logged-in user is automatically assigned as the farm owner during creation.  
- **Optional fields**: `description` and `established_date` can be left empty.  

---

## Testing

Automated tests available in tests/test_farms.py using pytest and APIClient.

Manual tests performed using curl commands. 

Example Request:

**Create a Farm**
```bash
curl -X POST http://127.0.0.1:8000/api/farms/ \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "name": "Green Valley Dairy",
  "location": "Nakuru County",
  "description": "A small family-owned dairy farm",
  "established_date": "2020-05-15"
}'
```
Response

``` json
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
Future Steps:

Consider allowing multiple farms per user in future versions.

Integrate staff and manager roles for farm access and permissions.





# Expenses-and-Inventory App

Tracks suppliers, inventory, purchases, usage, and farm expenses. Supports low-stock alerts, automatic expense creation from purchases, and summary reporting by category and supplier. All records are scoped to the authenticated user's farm.

---

## Model: `Supplier`


| Field           | Type          | Notes                                              |
| --------------- | ------------- | -------------------------------------------------- |
| `id`            | AutoField     | Primary key                                        |
| `farm`          | ForeignKey    | Links to `Farm`                                    |
| `name`          | CharField     | Supplier name; unique per farm (`unique_together`) |
| `supplier_type` | CharField     | `walk_in` / `b2b`                                  |
| `contact`       | CharField     | Optional; blank allowed                            |
| `notes`         | TextField     | Optional; blank allowed                            |
| `is_active`     | BooleanField  | Defaults to `True`; use `False` for deactivation   |
| `created_at`    | DateTimeField | Auto-set on creation                               |


---

## Model: `InventoryItem`


| Field               | Type          | Notes                                                            |
| ------------------- | ------------- | ---------------------------------------------------------------- |
| `id`                | AutoField     | Primary key                                                      |
| `farm`              | ForeignKey    | Links to `Farm`                                                  |
| `name`              | CharField     | Item name; unique per farm                                       |
| `item_type`         | CharField     | Expense category driver: `feed` / `supplement` / `vet` / `labor` |
| `unit`              | CharField     | Unit of measure, e.g. `kg`, `litres`, `bags`                     |
| `quantity_on_hand`  | DecimalField  | Current stock level; read-only via API                           |
| `reorder_threshold` | DecimalField  | Optional manual low-stock threshold                              |
| `is_active`         | BooleanField  | Defaults to `True`                                               |
| `created_at`        | DateTimeField | Auto-set on creation                                             |


---

## Model: `InventoryPurchase`


| Field            | Type          | Notes                                        |
| ---------------- | ------------- | -------------------------------------------- |
| `id`             | AutoField     | Primary key                                  |
| `inventory_item` | ForeignKey    | Links to `InventoryItem`                     |
| `quantity`       | DecimalField  | Quantity purchased                           |
| `unit_cost`      | DecimalField  | Cost per unit                                |
| `total_cost`     | DecimalField  | Computed in service (`quantity * unit_cost`) |
| `date`           | DateField     | Purchase date (db indexed)                   |
| `created_at`     | DateTimeField | Auto-set on creation                         |


---

## Model: `InventoryUsage`


| Field            | Type          | Notes                    |
| ---------------- | ------------- | ------------------------ |
| `id`             | AutoField     | Primary key              |
| `inventory_item` | ForeignKey    | Links to `InventoryItem` |
| `quantity_used`  | DecimalField  | Quantity consumed        |
| `date`           | DateField     | Usage date (db indexed)  |
| `created_at`     | DateTimeField | Auto-set on creation     |


---

## Model: `Expense`


| Field                | Type          | Notes                                                                          |
| -------------------- | ------------- | ------------------------------------------------------------------------------ |
| `id`                 | AutoField     | Primary key                                                                    |
| `farm`               | ForeignKey    | Links to `Farm`                                                                |
| `supplier`           | ForeignKey    | Optional; `on_delete=SET_NULL`                                                 |
| `inventory_item`     | ForeignKey    | Optional; `on_delete=SET_NULL`                                                 |
| `inventory_purchase` | OneToOneField | Optional link to the purchase that generated this expense                      |
| `category`           | CharField     | `feed` / `supplement` / `vet` / `labor`; derived for inventory-linked expenses |
| `amount`             | DecimalField  | Total expense amount                                                           |
| `date`               | DateField     | Expense date (db indexed)                                                      |
| `notes`              | TextField     | Optional; blank allowed                                                        |
| `created_at`         | DateTimeField | Auto-set on creation                                                           |


---

## Endpoints

All endpoints require `Authorization: Bearer <access_token>`.


| Method | Endpoint                            | Description                                                   |
| ------ | ----------------------------------- | ------------------------------------------------------------- |
| GET    | `/api/v1/suppliers/`                | List suppliers for the authenticated user's farm              |
| POST   | `/api/v1/suppliers/`                | Create a supplier (farm auto-assigned)                        |
| GET    | `/api/v1/suppliers/{id}/`           | Retrieve one supplier                                         |
| PUT    | `/api/v1/suppliers/{id}/`           | Full update of supplier                                       |
| PATCH  | `/api/v1/suppliers/{id}/`           | Partial update of supplier (e.g. deactivate with `is_active`) |
| DELETE | `/api/v1/suppliers/{id}/`           | Always blocked at API level (`405`)                           |
| GET    | `/api/v1/inventory/`                | List inventory items for the authenticated user's farm        |
| POST   | `/api/v1/inventory/`                | Create an inventory item (farm auto-assigned)                 |
| GET    | `/api/v1/inventory/{id}/`           | Retrieve one inventory item                                   |
| PUT    | `/api/v1/inventory/{id}/`           | Full update of inventory item                                 |
| PATCH  | `/api/v1/inventory/{id}/`           | Partial update of inventory item                              |
| DELETE | `/api/v1/inventory/{id}/`           | Delete an inventory item                                      |
| GET    | `/api/v1/inventory-purchases/`      | List inventory purchases                                      |
| POST   | `/api/v1/inventory-purchases/`      | Record a purchase, update stock, and auto-create an expense   |
| GET    | `/api/v1/inventory-purchases/{id}/` | Retrieve one inventory purchase                               |
| GET    | `/api/v1/inventory-usage/`          | List inventory usage records                                  |
| POST   | `/api/v1/inventory-usage/`          | Record stock usage and reduce quantity on hand                |
| GET    | `/api/v1/inventory-usage/{id}/`     | Retrieve one inventory usage record                           |
| GET    | `/api/v1/inventory/low-stock/`      | Return items at or below reorder threshold                    |
| GET    | `/api/v1/expenses/`                 | List expenses for the authenticated user's farm               |
| POST   | `/api/v1/expenses/`                 | Create a pure expense or inventory-linked expense             |
| GET    | `/api/v1/expenses/{id}/`            | Retrieve one expense                                          |
| PUT    | `/api/v1/expenses/{id}/`            | Full update of expense                                        |
| PATCH  | `/api/v1/expenses/{id}/`            | Partial update of expense                                     |
| DELETE | `/api/v1/expenses/{id}/`            | Delete an expense                                             |
| GET    | `/api/v1/expenses/summary/`         | Aggregate spending totals by category and supplier            |


---

### Create Supplier

`POST /api/v1/suppliers/`

**Request:**

```json
{
  "name": "AgroVet Ltd",
  "supplier_type": "walk_in"
}
```

**Response `201`:**

```json
{
  "id": 1,
  "farm": 1,
  "name": "AgroVet Ltd",
  "supplier_type": "walk_in",
  "contact": "",
  "notes": "",
  "is_active": true,
  "created_at": "2026-04-28T07:00:00Z"
}
```

**Validation error `400` — duplicate supplier on same farm:**

```json
{
  "name": ["A supplier with this name already exists for your farm."]
}
```

### Delete Supplier (Blocked)

`DELETE /api/v1/suppliers/{id}/`

**Response `405`:**

```json
{
  "detail": "Suppliers cannot be deleted. Set is_active=False to deactivate."
}
```

### Create Inventory Item

`POST /api/v1/inventory/`

**Request:**

```json
{
  "name": "Dairy Meal",
  "item_type": "feed",
  "unit": "kg",
  "reorder_threshold": "20.00"
}
```

**Response `201`:**

```json
{
  "id": 1,
  "farm": 1,
  "name": "Dairy Meal",
  "item_type": "feed",
  "unit": "kg",
  "quantity_on_hand": "0.00",
  "reorder_threshold": "20.00",
  "is_active": true,
  "created_at": "2026-04-28T07:05:00Z"
}
```

### Record Inventory Purchase

`POST /api/v1/inventory-purchases/`

**Request:**

```json
{
  "inventory_item": 1,
  "quantity": "50.00",
  "unit_cost": "10.00",
  "date": "2026-04-28"
}
```

**Response `201`:**

```json
{
  "id": 1,
  "inventory_item": 1,
  "quantity": "50.00",
  "unit_cost": "10.00",
  "total_cost": "500.00",
  "date": "2026-04-28",
  "created_at": "2026-04-28T07:10:00Z",
  "farm": 1
}
```

### Record Inventory Usage

`POST /api/v1/inventory-usage/`

**Request:**

```json
{
  "inventory_item": 1,
  "quantity_used": "30.00",
  "date": "2026-04-28"
}
```

**Response `201`:**

```json
{
  "id": 1,
  "inventory_item": 1,
  "quantity_used": "30.00",
  "date": "2026-04-28",
  "created_at": "2026-04-28T07:15:00Z"
}
```

**Validation error `400` — insufficient stock:**

```json
{
  "quantity_used": ["Insufficient stock on hand."]
}
```

### Low-Stock Endpoint

`GET /api/v1/inventory/low-stock/`

Returns items where `quantity_on_hand <= reorder_threshold`.

**Response `200`:**

```json
[
  {
    "id": 1,
    "farm": 1,
    "name": "Dairy Meal",
    "item_type": "feed",
    "unit": "kg",
    "quantity_on_hand": "15.00",
    "reorder_threshold": "20.00",
    "is_active": true,
    "created_at": "2026-04-28T07:05:00Z"
  }
]
```

### Create Expense

`POST /api/v1/expenses/`

**Request:**

```json
{
  "category": "vet",
  "amount": "300.00",
  "date": "2026-04-28",
  "notes": "Vet visit"
}
```

**Response `201`:**

```json
{
  "id": 1,
  "farm": 1,
  "supplier": null,
  "inventory_item": null,
  "inventory_purchase": null,
  "category": "vet",
  "amount": "300.00",
  "date": "2026-04-28",
  "notes": "Vet visit",
  "created_at": "2026-04-28T07:20:00Z"
}
```

### Expense Summary

`GET /api/v1/expenses/summary/`

Returns total spend plus grouped totals by category and supplier for the filtered queryset.

**Response `200`:**

```json
{
  "total_spend": 400.00,
  "by_category": [
    {
      "category": "feed",
      "total": 200.00,
      "count": 2
    },
    {
      "category": "vet",
      "total": 200.00,
      "count": 1
    }
  ],
  "by_supplier": [
    {
      "supplier_id": 1,
      "supplier_name": "AgroVet Ltd",
      "total": 300.00,
      "count": 1
    }
  ]
}
```

---

## Filtering

Expense, purchase, and usage endpoints support date-based filtering and targeted lookups.


| Endpoint                       | Param        | Format       | Description                                 |
| ------------------------------ | ------------ | ------------ | ------------------------------------------- |
| `/api/v1/expenses/`            | `category`   | string       | Exact expense category                      |
| `/api/v1/expenses/`            | `supplier`   | integer      | Exact supplier ID                           |
| `/api/v1/expenses/`            | `start_date` | `YYYY-MM-DD` | Expenses on or after this date              |
| `/api/v1/expenses/`            | `end_date`   | `YYYY-MM-DD` | Expenses on or before this date             |
| `/api/v1/expenses/summary/`    | `start_date` | `YYYY-MM-DD` | Summary includes expenses from this date    |
| `/api/v1/expenses/summary/`    | `end_date`   | `YYYY-MM-DD` | Summary includes expenses through this date |
| `/api/v1/inventory-purchases/` | `date`       | `YYYY-MM-DD` | Exact purchase date                         |
| `/api/v1/inventory-usage/`     | `date`       | `YYYY-MM-DD` | Exact usage date                            |


Example:

```
GET /api/v1/expenses/summary/?start_date=2026-04-01&end_date=2026-04-30
```

---

## Services

### `record_expense()`

Located in `services.py`. Handles direct expense creation and shared expense logic.

- Validates that `category` is provided for pure expenses
- Derives `category` automatically from `inventory_item.item_type` for inventory-linked expenses
- Persists and returns the created `Expense` instance

### `record_inventory_purchase()`

Handles stock increase and purchase-linked accounting.

- Validates that the inventory item belongs to the given farm
- Computes `total_cost = quantity * unit_cost`
- Creates an `InventoryPurchase`
- Updates `inventory_item.quantity_on_hand += quantity`
- Calls `record_expense()` automatically with category derived from `inventory_item.item_type`
- Returns the created purchase record and linked expense outcome through the generated accounting records

### `record_inventory_usage()`

Handles stock consumption.

- Validates that the inventory item belongs to the given farm
- Raises `ValidationError` if `quantity_used > quantity_on_hand`
- Creates an `InventoryUsage`
- Updates `inventory_item.quantity_on_hand -= quantity_used`
- Returns the created `InventoryUsage` instance

### `get_low_stock_items(farm)`

Returns inventory items needing restock attention.

- Filters items to the given farm
- Includes only rows where `reorder_threshold` is set
- Returns items where `quantity_on_hand <= reorder_threshold`

### `get_expense_summary(queryset)`

Receives an already-filtered `Expense` queryset from the viewset.

- Computes `total_spend` using the same `Coalesce`/`DecimalField` pattern as sales summary services
- Groups totals by category
- Groups totals by supplier
- Returns a dictionary with `total_spend`, `by_category`, and `by_supplier`

---

## Key Design Decisions

- `quantity_on_hand` is read-only via the API; only service functions update stock levels
- Every `InventoryPurchase` automatically creates a linked `Expense`
- For inventory-linked expenses, `Expense.category` is derived from `InventoryItem.item_type`, never from user input
- For pure cost expenses (such as `vet` and `labor`), `category` is required from user input
- Supplier hard delete is blocked at the API level; deactivation should be done via `is_active=False`
- `Expense -> Supplier` and `Expense -> InventoryItem` use `SET_NULL` so financial history is preserved even if linked records are removed
- Reorder threshold is configured manually per item; low-stock alerts exclude items where no threshold is set

---

## Permissions & Ownership

- All viewsets scope `get_queryset()` to records owned by `request.user` through farm relationships
- Cross-user object access returns `404` (not `403`) due to queryset scoping
- `perform_create()` on supplier, inventory item, and expense endpoints auto-assigns the farm from the authenticated user's first farm
- Inventory purchase and usage services enforce cross-model ownership integrity by rejecting items from another farm

---

## Notes

- `Supplier` enforces `unique_together = ("farm", "name")` — duplicate supplier names are allowed across different farms, but not within the same farm
- `inventory-purchases` and `inventory-usage` use hyphenated URLs to avoid DRF router conflicts with nested paths
- Phase 2 will replace manual reorder thresholds with computed average daily usage
- Tests available in `tests/test_expenses.py` using `pytest` and DRF's `APIClient`

---

## Development

See the [project README](../../README.md) for local setup, environment variables, and how to run the development server.
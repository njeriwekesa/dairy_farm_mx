## 🐄 Cattle Management

The Cattle Management module supports secure multi-tenant CRUD operations for farm livestock.

### Features

- Create cattle under owned farms only
- Retrieve individual cattle records
- List cattle filtered by authenticated farm ownership
- Update cattle details
- Prevent reassignment of cattle to another farm after creation
- Delete owned cattle
- Query filtering (e.g., by breed)

### Security & Data Integrity

- Users can only access cattle belonging to their own farms.
- Cross-user access returns 404 to prevent data leakage.
- Farm relationship becomes immutable after creation.
- Ownership enforced at queryset level.

### Test Coverage

The feature includes automated pytest coverage for:

- Create (success & forbidden cases)
- List with ownership filtering
- Retrieve (owner & non-owner cases)
- Update (allowed fields)
- Farm immutability enforcement
- Delete (owner & non-owner cases)
- Query parameter filtering

All tests pass and mirror manual API verification via curl.
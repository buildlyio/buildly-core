# Datamesh App Documentation

The `datamesh` app is a Django-based module designed to manage relationships and data joins between different logic modules and models. It provides functionality for defining relationships, managing join records, and aggregating data across services.

## Overview of Components

### 1. **Models**
The `models.py` file defines the core database models for the app:

#### **LogicModuleModel**
- Represents a model in a logic module.
- Fields:
  - `logic_module_endpoint_name`: Name of the logic module endpoint.
  - `model`: Name of the model.
  - `endpoint`: API endpoint for the model.
  - `lookup_field_name`: Field used for lookups (e.g., `id` or `uuid`).
  - `is_local`: Indicates if the model is local to the system.
- **Potential Issues**:
  - The `unique_together` constraints may not handle edge cases where endpoint names or models are renamed.

#### **Relationship**
- Represents a relationship between two `LogicModuleModel` instances.
- Fields:
  - `key`: Key used to identify the relationship in responses.
  - `origin_model` and `related_model`: Foreign keys to `LogicModuleModel`.
  - `fk_field_name`: Name of the foreign key field.
- **Potential Issues**:
  - Reverse relationship validation may not handle concurrent saves properly.

#### **JoinRecord**
- Represents a join between two records based on a `Relationship`.
- Fields:
  - `record_id`/`record_uuid`: Identifiers for the origin record.
  - `related_record_id`/`related_record_uuid`: Identifiers for the related record.
  - `organization`: Links the join to an organization.
- **Potential Issues**:
  - Complex constraints may lead to database errors if not carefully managed.
  - Lack of validation for edge cases (e.g., conflicting IDs and UUIDs).

---

### 2. **Views**
The `views.py` file defines API endpoints for managing the models.

#### **LogicModuleModelViewSet**
- Handles CRUD operations for `LogicModuleModel`.

#### **RelationshiplViewSet**
- Handles CRUD operations for `Relationship`.
- **Issue**: Typo in the class name (`RelationshiplViewSet` should be `RelationshipViewSet`).

#### **JoinRecordViewSet**
- Handles CRUD operations for `JoinRecord`.
- Includes filtering using `DjangoFilterBackend` and `JoinRecordFilter`.
- **Issues**:
  - Uses the deprecated `filter_class` attribute (should be `filterset_class`).
  - Redundant `filter_fields` attribute (fields are already defined in the filter).

---

### 3. **Serializers**
The `serializers.py` file defines serializers for the models.

#### **LogicModuleModelSerializer**
- Serializes all fields of `LogicModuleModel`.

#### **RelationshipSerializer**
- Serializes `Relationship` with nested `LogicModuleModel` serializers for `origin_model` and `related_model`.

#### **JoinRecordSerializer**
- Serializes `JoinRecord` with custom logic for creating and updating relationships.
- **Issues**:
  - The `_model_choices` and `_model_choices_map` are populated dynamically, which may cause performance issues for large datasets.
  - The `to_representation` method adds additional fields but may not handle edge cases where relationships are missing.

---

### 4. **Utilities**
The `utils.py` file provides helper functions for managing joins and relationships.

#### Key Functions:
- `prepare_lookup_kwargs`: Prepares lookup arguments based on the direction of the relationship.
- `validate_join`: Validates and creates a join if it doesn't exist.
- `join_record`: Creates a new join record.
- `delete_join_record`: Deletes join records based on primary keys.
- **Issues**:
  - Lack of error handling for invalid inputs.
  - Functions like `validate_primary_key` assume specific formats for IDs and UUIDs, which may not always hold true.

---

### 5. **Services**
The `services.py` file defines the `DataMesh` class for aggregating data across services.

#### Key Features:
- Retrieves related records and metadata.
- Extends data with nested relationships.
- Supports asynchronous data aggregation.
- **Issues**:
  - The `_extend_with_local` method assumes that local models are always accessible, which may not be true in all cases.
  - Lack of validation for access control in `_extend_with_local`.
  - Error handling for external service requests is minimal.

---

### 6. **Filters**
The `filters.py` file defines the `JoinRecordFilter` for filtering `JoinRecord` instances.

#### Key Features:
- Supports filtering by `record_id`, `record_uuid`, `related_record_id`, and `related_record_uuid`.

---

### 7. **Managers**
The `managers.py` file defines custom model managers.

#### Key Features:
- `LogicModuleModelManager`: Provides a method for retrieving models by concatenated names.
- `JoinRecordManager`: Provides a method for retrieving join records based on relationships and primary keys.

---

### 8. **Mixins**
The `mixins.py` file defines the `OrganizationQuerySetMixin`.

#### Key Features:
- Filters querysets based on the `organization_uuid` in the session.
- **Issues**:
  - Assumes the presence of `jwt_organization_uuid` in the session, which may not always be set.

---

### 9. **Admin**
The `admin.py` file registers the models (`LogicModuleModel`, `Relationship`, `JoinRecord`) with the Django admin site.

---

### 10. **URLs**
The `urls.py` file defines API routes using a `SimpleRouter`.

---

### 11. **Exceptions**
The `exceptions.py` file defines a custom exception (`DatameshConfigurationError`) for configuration errors.

---

## Potential Issues and TODOs


1. **Error Handling**
   - Add error handling for invalid inputs in utility functions and services.

2. **Performance**
   - Optimize dynamic population of `_model_choices` in `JoinRecordSerializer`.

3. **Pagination**
   - Add pagination to viewsets to handle large datasets efficiently.

4. **Concurrency**
    - Ensure thread safety in methods like `validate_reverse_relationship_absence`.

---

## Example Usage

### Fetching Logic Module Models
```bash
GET /api/logicmodulemodels/
```

### Creating a Relationship
```bash
POST /api/relationships/
{
    "origin_model_id": "uuid-of-origin-model",
    "related_model_id": "uuid-of-related-model",
    "key": "example_relationship_key"
}
```

### Filtering Join Records
```bash
GET /api/joinrecords/?relationship__key=example_key&record_id=123
```

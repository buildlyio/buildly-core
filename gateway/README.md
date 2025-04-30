# REST Endpoint Aggregator Documentation

The **REST Endpoint Aggregator** is a Django-based app designed to aggregate and manage API specifications (Swagger/OpenAPI) from multiple microservices. It provides functionality to fetch, merge, and version API specifications, enabling seamless integration and routing of requests through a centralized gateway.

---

## Overview of Components

### 1. **Swagger Aggregation**
The `SwaggerAggregator` class in `aggregator.py` is the core of the app. It fetches Swagger specifications from remote APIs, detects changes, and updates the database with the latest specifications and versions.

#### Key Features:
- **Fetch Swagger Specifications**:
  - Retrieves Swagger documents from remote APIs using URLs defined in the configuration.
  - Uses the `utils.get_swagger_from_url` function to fetch Swagger files.
- **Change Detection**:
  - Compares the stored Swagger document and version with the latest fetched version.
  - Uses a hash-based comparison (`_get_hash`) to detect changes in the document.
- **Version Logging**:
  - Updates the `LogicModule` model with the new Swagger document and version.
  - Logs version changes in the `SwaggerVersionHistory` model for auditing purposes.
- **Swagger Merging**:
  - Merges multiple Swagger documents into a single aggregated document.
  - Renames definitions and paths to avoid collisions between APIs.
- **Operation ID Generation**:
  - Replaces operation IDs in the Swagger document to avoid collisions.

#### Changes Made:
- **Hash-Based Comparison**:
  - Added `_get_hash` to generate a hash of the Swagger document for efficient comparison.
- **Version Logging**:
  - Added logic to log version changes in the `SwaggerVersionHistory` model.
- **Error Handling**:
  - Improved error handling for connection, timeout, and invalid response errors.

---

### 2. **Gateway Views**
The `APIGatewayView` and `APIAsyncGatewayView` classes in `views.py` handle incoming API requests and route them to the appropriate microservices.

#### Key Features:
- **Request Validation**:
  - Validates incoming requests before forwarding them to the target service.
- **Request Routing**:
  - Routes requests to the appropriate microservice based on the service and model specified in the URL.
- **Response Handling**:
  - Aggregates responses from multiple services if required (e.g., for `join` or `extend` operations).
- **Asynchronous Support**:
  - The `APIAsyncGatewayView` class provides asynchronous request handling using `aiohttp`.

---

### 3. **Utilities**
The `utils.py` file provides helper functions for constructing Swagger URLs, fetching Swagger documents, and validating object access.

#### Key Functions:
- `get_swagger_url_by_logic_module`: Constructs the Swagger URL for a given `LogicModule`.
- `get_swagger_from_url`: Fetches the Swagger document from a given URL.
- `valid_uuid4`: Validates if a string is a valid UUID4.

---

### 4. **Clients**
The `clients.py` file defines synchronous and asynchronous Swagger clients for interacting with microservices.

#### Key Features:
- **SwaggerClient**:
  - Uses the `requests` library for synchronous requests.
- **AsyncSwaggerClient**:
  - Uses the `aiohttp` library for asynchronous requests.
- **Request Validation**:
  - Validates requests against the Swagger specification before sending them to the service.

---

### 5. **Models**
The `models.py` file defines the `SwaggerVersionHistory` model for tracking changes in Swagger versions.

#### **SwaggerVersionHistory**
- Fields:
  - `endpoint_name`: The name of the endpoint.
  - `old_version`: The previous version of the Swagger document.
  - `new_version`: The new version of the Swagger document.
  - `changed_at`: The timestamp when the change occurred.
- **Purpose**:
  - Logs version changes for auditing and debugging purposes.

---

### 6. **Permissions**
The `permissions.py` file defines the `AllowLogicModuleGroup` permission class, which restricts access to services based on user roles and permissions.

---

### 7. **Schema Generation**
The `generator.py` file defines the `OpenAPISchemaGenerator` class, which integrates the aggregated Swagger document into the API gateway's schema.

---

## How It Works

1. **Swagger Aggregation**:
   - The `SwaggerAggregator` fetches Swagger documents from remote APIs.
   - It detects changes in the documents and updates the `LogicModule` model with the latest specifications and versions.
   - Version changes are logged in the `SwaggerVersionHistory` model.

2. **Request Routing**:
   - Incoming requests are routed to the appropriate microservice based on the service and model specified in the URL.
   - The `APIGatewayView` validates the request and forwards it to the target service.

3. **Response Handling**:
   - Responses from microservices are aggregated if required (e.g., for `join` or `extend` operations).
   - The aggregated response is returned to the client.

4. **Schema Generation**:
   - The `OpenAPISchemaGenerator` integrates the aggregated Swagger document into the API gateway's schema.

---

## TODO List

### **Performance Improvements**
1. **Parallel Fetching of Swagger Documents**:
   - Use asynchronous requests (e.g., `aiohttp`) to fetch Swagger documents in parallel.
   - This will reduce the time taken to aggregate Swagger documents from multiple services.

2. **Caching**:
   - Cache fetched Swagger documents locally (e.g., using Redis) to reduce repeated API calls.
   - Cache aggregated Swagger documents to avoid recomputation.

3. **Batch Database Updates**:
   - Use Django's `bulk_update` for updating multiple `LogicModule` entries at once.

4. **Optimize JSON Operations**:
   - Avoid unnecessary serialization and deserialization of Swagger documents during merging.

---

### **Logic Improvements**
1. **Error Handling**:
   - Add retries for failed API calls to handle transient network issues.
   - Log detailed error messages for debugging.

2. **Validation**:
   - Validate the structure of fetched Swagger documents before processing them.
   - Ensure that required fields (e.g., `info.version`) are present in the document.

3. **Conflict Resolution**:
   - Handle conflicts in definitions and paths during Swagger merging more gracefully.

4. **Pagination Support**:
   - Add support for paginated responses when aggregating data from multiple services.

---

### **Testing**
1. **Unit Tests**:
   - Write unit tests for all utility functions, views, and models.
   - Test edge cases, such as invalid Swagger documents and missing fields.

2. **Integration Tests**:
   - Test the entire aggregation and routing workflow with multiple microservices.

3. **Performance Tests**:
   - Measure the time taken to fetch and aggregate Swagger documents for a large number of services.

---

## Example Usage

### Fetching Swagger Documents
```python
aggregator = SwaggerAggregator(configuration)
swagger_docs = aggregator.get_aggregate_swagger()
```

### Routing Requests
```bash
GET /timetracking/timeevent/123/
```

### Viewing Version History
```bash
GET /admin/gateway/swaggerversionhistory/
```
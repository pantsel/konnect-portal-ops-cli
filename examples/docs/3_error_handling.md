# 3. Error Handling

The API provides detailed error responses for invalid requests. Below is a summary of potential errors:

| HTTP Status Code | Description             |
|------------------|-------------------------|
| 400              | Bad Request             |
| 401              | Unauthorized            |
| 403              | Forbidden               |
| 500              | Internal Server Error   |

**Example Error Response:**
```json
{
  "error": "Bad Request",
  "message": "Invalid query parameters."
}
```

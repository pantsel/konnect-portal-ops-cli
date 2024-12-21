# HTTPBin API Documentation

## Overview

**Title:** HTTPBin API  
**Version:** 1.0.0  
**Base URL:** https://example.com  

The HTTPBin API provides a simple interface to make requests to the `/httpbin` endpoint and retrieve information about the request such as URL, headers, and query parameters.

---

## Authentication

This API supports the following authentication methods:

1. **Basic Authentication**  
   Use HTTP Basic Authentication with a username and password.

2. **OpenID Connect**  
   Endpoint: [OpenID Configuration](https://login.microsoftonline.com/96566719-5c4d-4e3a-8944-47eb10e03365/v2.0/.well-known/openid-configuration)

---

## Endpoints

### 1. **GET /httpbin**

**Description:**
Retrieves data from the HTTPBin endpoint.

**Tags:** HTTPBin

#### Security:
- OpenID Connect (`openIdAuth`)
- Basic Authentication (`basicAuth`)

#### Responses:

- **200 OK**  
  A successful response containing the details of the request.

  **Response Body:**
  ```json
  {
    "url": "string",
    "args": {
      "<key>": "string"
    },
    "headers": {
      "<key>": "string"
    }
  }
  ```

  **Schema Details:**
  - `url` (string): The URL of the request.
  - `args` (object): Query parameters sent in the request. Keys and values are strings.
  - `headers` (object): Headers sent in the request. Keys and values are strings.

- **400 Bad Request**  
  Returned when the request is invalid.

---

## Components

### Security Schemes

#### 1. Basic Authentication (`basicAuth`)
- Type: HTTP
- Scheme: Basic

#### 2. OpenID Connect (`openIdAuth`)
- OpenID Connect URL: [OpenID Configuration](https://myidp.com/.well-known/openid-configuration)

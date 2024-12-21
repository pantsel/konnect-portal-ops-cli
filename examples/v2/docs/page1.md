# HTTPBin API Documentation

## Overview

**Title:** HTTPBin API  
**Version:** 2.0.0  
**Base URLs:**
- https://example.com
- https://example.org

The HTTPBin API provides endpoints to retrieve or post data, allowing for inspection of request details such as URL, headers, and query parameters.

---

## Authentication

This API supports the following authentication methods:

1. **Basic Authentication**  
   Use HTTP Basic Authentication with a username and password.

2. **OpenID Connect**  
   Endpoint: [OpenID Configuration](https://myidp.com/.well-known/openid-configuration)

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

### 2. **POST /httpbin**

**Description:**
Posts data to the HTTPBin endpoint.

**Tags:** HTTPBin

#### Security:
- OpenID Connect (`openIdAuth`)
- Basic Authentication (`basicAuth`)

#### Request Body:
- **Required:** Yes
- **Content Type:** `application/json`
- **Schema:**

  ```json
  {
    "data": "string"
  }
  ```

  **Details:**
  - `data` (string): The data to post.

#### Responses:

- **200 OK**  
  A successful response containing the details of the request and posted data.

  **Response Body:**
  ```json
  {
    "url": "string",
    "args": {
      "<key>": "string"
    },
    "headers": {
      "<key>": "string"
    },
    "json": {
      "<key>": "string"
    }
  }
  ```

  **Schema Details:**
  - `url` (string): The URL of the request.
  - `args` (object): Query parameters sent in the request. Keys and values are strings.
  - `headers` (object): Headers sent in the request. Keys and values are strings.
  - `json` (object): JSON data sent in the request. Keys and values are strings.

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

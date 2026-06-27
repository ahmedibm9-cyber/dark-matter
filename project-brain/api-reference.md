# API Reference

> This document defines the API philosophy, standards, and complete endpoint reference for the project. It serves as the canonical source of truth for frontend developers, mobile developers, integrators, and QA engineers.

---

## 1. API Design Philosophy

### Principles

1. **Consistency over convenience:** Every endpoint follows the same patterns. Predictability reduces errors and speeds up integration.
2. **Explicit over implicit:** Everything is named clearly. No magic values, no hidden behavior, no undocumented defaults.
3. **Backward compatibility:** Breaking changes are avoided unless absolutely necessary. Deprecation is communicated with a minimum 6-month migration window.
4. **Self-descriptive:** Responses include enough metadata (links, pagination info, status) for clients to navigate without out-of-band knowledge.
5. **Idempotent where possible:** GET, PUT, DELETE are idempotent. POST is not idempotent unless explicitly documented with an idempotency key.
6. **Error-rich:** Errors include machine-readable codes and human-readable messages with actionable details.

### API Style

- **Primary protocol:** REST over HTTPS
- **Secondary protocol:** WebSocket for real-time events (notifications, status updates)
- **Content type:** `application/json` for requests and responses
- **Character encoding:** UTF-8

---

## 2. Authentication and Authorization

### Authentication Methods

| Method | Endpoint | Token Type | Usage |
|---|---|---|---|
| Email + Password | `POST /api/v1/auth/login` | JWT (Bearer) | Web and mobile apps |
| OAuth 2.0 / SSO | `POST /api/v1/auth/oauth` | JWT (Bearer) | Social login, enterprise SSO |
| API Key | Header `X-API-Key` | Opaque string | Server-to-server integration |
| Refresh Token | `POST /api/v1/auth/refresh` | Opaque string (httpOnly cookie) | Session renewal |

### Token Format

```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIs...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4=",
  "expiresIn": 900,
  "tokenType": "Bearer"
}
```

### Token Validation

Every protected endpoint validates:
1. Token presence in `Authorization: Bearer <token>` header
2. Token signature (RS256 with public key)
3. Token expiry (`exp` claim)
4. Token issuer (`iss` claim — must match configured value)
5. Token audience (`aud` claim — must match API identifier)

### Authorization Model

- **RBAC (Role-Based Access Control):** Each user has a role (`user`, `moderator`, `admin`).
- **Permission checks** are performed at the API middleware layer.
- **Resource ownership** is enforced at the service layer.
- **Scope-based tokens** for OAuth (e.g., `read:orders`, `write:products`).

### Authentication Headers

| Header | Required For | Format | Example |
|---|---|---|---|
| `Authorization` | All protected endpoints | `Bearer <token>` | `Bearer eyJhbGciOiJSUzI1NiIs...` |
| `X-API-Key` | Server-to-server endpoints | `<api-key>` | `sk_live_abc123def456` |
| `Idempotency-Key` | POST, PUT, PATCH (idempotent callers) | UUID v4 | `uuid-abc-123-def-456` |

---

## 3. Rate Limiting Strategy

### Rate Limit Tiers

| Tier | Scope | Rate Limit | Burst | Applied To |
|---|---|---|---|---|
| Public | Per IP address | 100 req/min | 20 req | Unauthenticated endpoints |
| Authenticated | Per user ID | 1000 req/min | 50 req | Authenticated user endpoints |
| Admin | Per admin user | 5000 req/min | 100 req | Admin endpoints |
| Webhook | Per source IP | 100 req/min | 10 req | Webhook receivers |
| Partner API | Per API key | 10000 req/min | 200 req | Partner integration endpoints |

### Rate Limit Headers

Every response includes:

| Header | Description | Example |
|---|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the window | `1000` |
| `X-RateLimit-Remaining` | Requests remaining in the window | `842` |
| `X-RateLimit-Reset` | Unix timestamp when the window resets | `1704067200` |
| `Retry-After` | Seconds to wait before retrying (only on 429) | `30` |

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please wait before retrying.",
    "details": {
      "retryAfter": 30,
      "limit": 1000,
      "windowSeconds": 60
    }
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Rate Limit Exceptions

- **Health checks** (`/health`, `/readiness`) are not rate limited.
- **Webhook receivers** have separate limits.
- **Trusted partners** can request higher limits (subject to review).

---

## 4. Endpoint Groups

### Base URL

```
Production: https://api.[project].com/v1
Staging:    https://api-staging.[project].com/v1
```

### Endpoint Documentation Template

Each endpoint is documented as follows:

```markdown
### [HTTP_METHOD] [PATH]

**Description:** [One to two sentence description of what this endpoint does.]

**Authentication:** [Required / Optional / None]
**Rate Limit Tier:** [Public / Authenticated / Admin / Partner]

#### Request

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| [param] | [type] | Yes/No | [Description] |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| [param] | [type] | Yes/No | [default] | [Description] |

**Request Body:**

```json
{
  "field1": "value1",
  "field2": 123
}
```

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| field1 | string | Yes | min 1, max 255 | [Description] |
| field2 | integer | No | min 0, max 1000000 | [Description] |

#### Response

**Status Code:** [201 / 200 / 204 / etc.]

**Response Body:**

```json
{
  "success": true,
  "data": {
    "id": "uuid-abc-123",
    "field1": "value1",
    "createdAt": "2024-01-01T12:00:00Z"
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### Errors

| Status Code | Error Code | Condition |
|---|---|---|
| 400 | VALIDATION_ERROR | Invalid input data |
| 401 | UNAUTHENTICATED | Missing or invalid auth token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource state conflict |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |

#### Example

```bash
curl -X POST https://api.example.com/v1/[resource] \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"field1": "value1", "field2": 123}'
```
```

---

### 4.1 Authentication Endpoints

---

#### POST /api/v1/auth/register

**Description:** Create a new user account.

**Authentication:** None
**Rate Limit Tier:** Public

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "ValidP@ss123",
  "name": "John Doe"
}
```

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| email | string | Yes | Valid email format, max 255 chars | User's email address |
| password | string | Yes | Min 8 chars, 1 upper, 1 lower, 1 digit, 1 special | User's password |
| name | string | Yes | Min 1, max 100 chars | User's display name |

**Response:** `201 Created`

```json
{
  "success": true,
  "data": {
    "id": "uuid-abc-123",
    "email": "user@example.com",
    "name": "John Doe",
    "status": "pending",
    "createdAt": "2024-01-01T12:00:00Z"
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Errors:**

| Code | Condition |
|---|---|
| VALIDATION_ERROR | Invalid email or weak password |
| CONFLICT | Email already registered |

---

#### POST /api/v1/auth/login

**Description:** Authenticate with email and password, receive access and refresh tokens.

**Authentication:** None
**Rate Limit Tier:** Public (strict — 5 attempts per minute per IP)

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "ValidP@ss123"
}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJSUzI1NiIs...",
    "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4=",
    "expiresIn": 900,
    "tokenType": "Bearer",
    "user": {
      "id": "uuid-abc-123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user"
    }
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Errors:**

| Code | Condition |
|---|---|
| VALIDATION_ERROR | Missing email or password |
| UNAUTHENTICATED | Invalid credentials |
| FORBIDDEN | Account suspended or disabled |
| RATE_LIMIT_EXCEEDED | Too many login attempts |

---

#### POST /api/v1/auth/refresh

**Description:** Exchange a refresh token for new access and refresh tokens.

**Authentication:** Refresh token (httpOnly cookie or request body)
**Rate Limit Tier:** Authenticated

**Request Body:**

```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4="
}
```

**Response:** `200 OK` (same format as login)

---

#### POST /api/v1/auth/logout

**Description:** Invalidate the current session (refresh token).

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Request Body:**

```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4="
}
```

**Response:** `204 No Content`

---

#### POST /api/v1/auth/oauth

**Description:** Authenticate via OAuth 2.0 provider (Google, GitHub, etc.).

**Authentication:** None
**Rate Limit Tier:** Public

**Request Body:**

```json
{
  "provider": "google",
  "code": "oauth_authorization_code",
  "redirectUri": "https://app.example.com/auth/callback"
}
```

**Response:** `200 OK` (same format as login)

---

### 4.2 User Endpoints

---

#### GET /api/v1/users/me

**Description:** Get the authenticated user's profile.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "uuid-abc-123",
    "email": "user@example.com",
    "name": "John Doe",
    "avatarUrl": "https://cdn.example.com/avatars/uuid-abc-123.jpg",
    "role": "user",
    "status": "active",
    "emailVerifiedAt": "2024-01-01T12:00:00Z",
    "lastLoginAt": "2024-01-15T08:30:00Z",
    "createdAt": "2024-01-01T12:00:00Z"
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

---

#### PATCH /api/v1/users/me

**Description:** Update the authenticated user's profile.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Request Body:**

```json
{
  "name": "Jane Doe",
  "avatarUrl": "https://cdn.example.com/avatars/new-avatar.jpg"
}
```

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| name | string | No | Min 1, max 100 | Display name |
| avatarUrl | string | No | Valid URL, max 500 chars | Profile picture URL |

**Response:** `200 OK` (user object)

---

#### DELETE /api/v1/users/me

**Description:** Request deletion of the authenticated user's account.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Response:** `202 Accepted`

```json
{
  "success": true,
  "data": {
    "message": "Account deletion scheduled. You have 30 days to cancel.",
    "deletionScheduledAt": "2024-02-15T12:00:00Z"
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-15T12:00:00Z"
  }
}
```

---

### 4.3 Product Endpoints

---

#### GET /api/v1/products

**Description:** List products with pagination, filtering, and sorting.

**Authentication:** Optional (authenticated users see personalized pricing)
**Rate Limit Tier:** Public

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| page | integer | No | 1 | Page number (1-indexed) |
| pageSize | integer | No | 20 | Items per page (max 100) |
| sortBy | string | No | createdAt | Sort field (name, price, createdAt, rating) |
| sortOrder | string | No | desc | Sort direction (asc, desc) |
| category | string | No | — | Filter by category slug |
| search | string | No | — | Full-text search query |
| minPrice | number | No | — | Minimum price filter |
| maxPrice | number | No | — | Maximum price filter |
| inStock | boolean | No | — | Filter by stock availability |
| cursor | string | No | — | Cursor for keyset pagination |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-prod-001",
      "name": "Wireless Headphones",
      "slug": "wireless-headphones",
      "description": "Premium noise-cancelling wireless headphones",
      "price": 149.99,
      "currency": "USD",
      "compareAtPrice": 199.99,
      "stock": 42,
      "productType": "physical",
      "category": {
        "id": "uuid-cat-001",
        "name": "Electronics",
        "slug": "electronics"
      },
      "images": [
        {
          "url": "https://cdn.example.com/products/headphones-1.jpg",
          "alt": "Wireless Headphones - Front View"
        }
      ],
      "rating": 4.5,
      "reviewCount": 128,
      "tags": ["audio", "bluetooth", "noise-cancelling"],
      "createdAt": "2024-01-01T12:00:00Z"
    }
  ],
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z",
    "page": 1,
    "pageSize": 20,
    "totalItems": 150,
    "totalPages": 8,
    "hasNextPage": true,
    "hasPreviousPage": false
  }
}
```

---

#### GET /api/v1/products/:id

**Description:** Get a single product by ID or slug.

**Authentication:** Optional
**Rate Limit Tier:** Public

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Product UUID or slug |

**Response:** `200 OK` (single product object)

**Errors:**

| Code | Condition |
|---|---|
| NOT_FOUND | Product does not exist |

---

#### POST /api/v1/products

**Description:** Create a new product (admin only).

**Authentication:** Required (admin or product_manager role)
**Rate Limit Tier:** Admin

**Request Body:**

```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 29.99,
  "currency": "USD",
  "stock": 100,
  "categoryId": "uuid-cat-001",
  "images": [
    {
      "url": "https://cdn.example.com/products/new-1.jpg",
      "alt": "New Product - Front View"
    }
  ],
  "tags": ["new", "featured"]
}
```

**Response:** `201 Created` (product object)

---

#### PATCH /api/v1/products/:id

**Description:** Update a product (admin only).

**Authentication:** Required (admin or product_manager role)
**Rate Limit Tier:** Admin

---

#### DELETE /api/v1/products/:id

**Description:** Soft-delete a product (admin only).

**Authentication:** Required (admin role)
**Rate Limit Tier:** Admin

**Response:** `204 No Content`

---

### 4.4 Order Endpoints

---

#### POST /api/v1/orders

**Description:** Create a new order from the current cart.

**Authentication:** Required
**Rate Limit Tier:** Authenticated
**Idempotency:** Supported via `Idempotency-Key` header

**Request Body:**

```json
{
  "shippingAddressId": "uuid-addr-001",
  "billingAddressId": "uuid-addr-001",
  "items": [
    {
      "productId": "uuid-prod-001",
      "quantity": 2
    },
    {
      "productId": "uuid-prod-002",
      "quantity": 1
    }
  ],
  "couponCode": "SAVE10",
  "notes": "Leave at the front door"
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "data": {
    "id": "uuid-order-001",
    "status": "pending",
    "items": [
      {
        "productId": "uuid-prod-001",
        "name": "Wireless Headphones",
        "quantity": 2,
        "unitPrice": 149.99,
        "total": 299.98
      }
    ],
    "subtotal": 449.97,
    "shippingCost": 9.99,
    "tax": 36.00,
    "discount": -44.99,
    "total": 450.97,
    "currency": "USD",
    "shippingAddress": {},
    "billingAddress": {},
    "estimatedDelivery": "2024-01-08",
    "createdAt": "2024-01-01T12:00:00Z",
    "paymentUrl": "https://pay.example.com/order/uuid-order-001"
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

---

#### GET /api/v1/orders

**Description:** List the authenticated user's orders.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| status | string | No | — | Filter by status (pending, confirmed, etc.) |
| page | integer | No | 1 | Page number |
| pageSize | integer | No | 20 | Items per page |

---

#### GET /api/v1/orders/:id

**Description:** Get a single order by ID.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Note:** Regular users can only access their own orders. Admins can access all orders.

---

#### POST /api/v1/orders/:id/cancel

**Description:** Cancel an order.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

**Request Body:**

```json
{
  "reason": "Changed my mind"
}
```

**Response:** `200 OK`

---

### 4.5 Cart Endpoints

---

#### GET /api/v1/cart

**Description:** Get the authenticated user's current cart.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

---

#### POST /api/v1/cart/items

**Description:** Add an item to the cart.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

```json
{
  "productId": "uuid-prod-001",
  "quantity": 1
}
```

---

#### PATCH /api/v1/cart/items/:itemId

**Description:** Update cart item quantity.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

```json
{
  "quantity": 3
}
```

---

#### DELETE /api/v1/cart/items/:itemId

**Description:** Remove an item from the cart.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

---

### 4.6 Payment Endpoints

---

#### POST /api/v1/payments/intent

**Description:** Create a payment intent for an order.

**Authentication:** Required
**Rate Limit Tier:** Authenticated

```json
{
  "orderId": "uuid-order-001",
  "paymentMethodId": "pm_abc123"
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "data": {
    "paymentIntentId": "pi_xyz789",
    "clientSecret": "pi_xyz789_secret_abc123",
    "amount": 450.97,
    "currency": "USD",
    "status": "requires_payment_method"
  }
}
```

---

### 4.7 Webhook Endpoints

---

#### POST /api/v1/webhooks/payments

**Description:** Receive payment processor webhook events.

**Authentication:** HMAC signature verification (not Bearer token)
**Rate Limit Tier:** Webhook

**Headers:**

| Header | Description |
|---|---|
| `Stripe-Signature` / `X-Webhook-Signature` | HMAC signature for verification |

**Request Body:** (varies by processor — raw event payload)

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "received": true
  }
}
```

**Important:**
- Always verify the webhook signature before processing.
- Respond with 200 quickly — extended processing should be done asynchronously.
- Webhook handlers must be idempotent (check event ID before processing).
- Duplicate events are acknowledged but not re-processed.

---

#### POST /api/v1/webhooks/email

**Description:** Receive email delivery status events (bounces, complaints, opens).

**Authentication:** HMAC signature verification
**Rate Limit Tier:** Webhook

**Request Body:** (SendGrid / SES event format)

**Response:** `200 OK`

---

## 5. Request/Response Format Standards

### Request Format

- **Content-Type:** `application/json` (for all requests with a body)
- **Accept:** `application/json`
- **Body:** JSON object or array
- **Dates:** ISO 8601 in UTC (`2024-01-01T12:00:00Z`)
- **Monetary values:** Decimal numbers (not strings), 2 decimal places

### Response Envelope

All responses follow a consistent envelope:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "requestId": "req_[uuid]",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

| Field | Type | Always Present | Description |
|---|---|---|---|
| success | boolean | Yes | True for success responses |
| data | object / array / null | Yes (null for 204) | Response payload |
| error | object | No (only on failure) | Error details |
| meta.requestId | string | Yes | Unique request identifier |
| meta.timestamp | string | Yes | ISO 8601 timestamp |

### Response Status Codes

| Code | Meaning | When |
|---|---|---|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Async operation accepted (deletion, processing) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, malformed input |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource state conflict (duplicate, stale) |
| 422 | Unprocessable Entity | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Downstream dependency failure |

---

## 6. Error Format Standards

### Error Response Structure

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request was invalid.",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters",
        "code": "TOO_SHORT"
      }
    ]
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Error Codes

| Error Code | HTTP Status | Description |
|---|---|---|
| VALIDATION_ERROR | 400 | Input validation failed |
| UNAUTHENTICATED | 401 | Not authenticated |
| TOKEN_EXPIRED | 401 | Access token has expired |
| TOKEN_INVALID | 401 | Token is malformed or invalid |
| FORBIDDEN | 403 | Insufficient permissions |
| RESOURCE_NOT_FOUND | 404 | Requested resource not found |
| CONFLICT | 409 | Resource state conflict |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Unexpected server error |
| DEPENDENCY_FAILURE | 503 | Downstream service unavailable |
| BUSINESS_RULE_VIOLATION | 422 | Business rule prevented operation |

### Error Response Guidelines

- **Do not expose stack traces** in production responses.
- **Do not reveal existence of resources** the user does not have access to (return 404, not 403).
- **Do include correlation IDs** so errors can be traced in logs.
- **Do provide actionable error messages** that help the developer fix the request.
- **Do include field-level errors** for validation failures.

---

## 7. Pagination Standards

### Offset-Based Pagination (Default)

**Request:**
```
GET /api/v1/products?page=1&pageSize=20
```

**Response Meta:**

```json
"meta": {
  "page": 1,
  "pageSize": 20,
  "totalItems": 150,
  "totalPages": 8,
  "hasNextPage": true,
  "hasPreviousPage": false
}
```

### Cursor-Based Pagination (For Large Datasets)

**Request:**
```
GET /api/v1/products?cursor=eyJpZCI6InV1aWQtcHJvZC0wMDEifQ==&pageSize=20
```

**Response Meta:**

```json
"meta": {
  "pageSize": 20,
  "cursor": "eyJpZCI6InV1aWQtcHJvZC0wMDEifQ==",
  "nextCursor": "eyJpZCI6InV1aWQtcHJvZC0wMjEifQ==",
  "hasNextPage": true
}
```

### Pagination Rules

- `pageSize` defaults to 20, maximum 100.
- `page` is 1-indexed.
- Cursor is a base64-encoded JSON object containing the last item's ID.
- Cursor-based pagination is preferred for collections that exceed 10,000 items.
- Offset-based pagination is preferred for smaller collections.

---

## 8. Versioning Strategy

### URL Path Versioning

API versions are specified in the URL path:

```
https://api.example.com/v1/products
https://api.example.com/v2/products
```

### Version Lifecycle

| Phase | Description | Duration |
|---|---|---|
| Preview | Early access, may change without notice | 1-3 months |
| Stable | Fully supported, no breaking changes | 12+ months |
| Deprecated | Still functional but no new features | 6 months |
| Sunset | Removed from production | — |

### Versioning Policy

- **Major versions** (v1 -> v2): Breaking changes. Minimum 6 months notice before deprecation. At least one major version overlap (v1 and v2 both available while v1 is deprecated).
- **Minor versions** (v1.1 -> v1.2): Backward-compatible additions. New fields in responses, new optional parameters, new endpoints.
- **No patch-level versioning** at the API level (use HTTP headers for patch-level changes).

### Deprecation Headers

Deprecated endpoints return these headers:

| Header | Example | Description |
|---|---|---|
| `Sunset` | `Sat, 01 Jan 2025 00:00:00 GMT` | Date when endpoint will be removed |
| `Deprecation` | `true` | Indicates this endpoint is deprecated |
| `Link` | `</v2/products>; rel="successor-version"` | Link to the replacement |

---

## 9. Webhook Documentation Template

### Standard Webhook Payload

```json
{
  "eventId": "evt_abc123",
  "eventType": "order.created",
  "eventVersion": "1.0",
  "createdAt": "2024-01-01T12:00:00Z",
  "data": {}
}
```

### Webhook Event Catalog

| Event Type | Description | Trigger | Payload |
|---|---|---|---|
| order.created | Order has been created | POST /api/v1/orders | Order object |
| order.confirmed | Payment confirmed, order processing | Payment webhook | Order object |
| order.shipped | Order has shipped | Fulfillment system | Order + tracking |
| order.delivered | Order delivered | Carrier webhook | Order + delivery proof |
| order.cancelled | Order cancelled | User or admin action | Order + cancel reason |
| payment.succeeded | Payment successful | Payment processor | Payment + order |
| payment.failed | Payment failed | Payment processor | Payment + error |
| user.registered | New user registered | POST /api/v1/auth/register | User object |
| user.deleted | User account deleted | DELETE /api/v1/users/me | User ID |
| product.updated | Product details changed | PATCH /api/v1/products/:id | Product diff |

### Webhook Delivery

- **Delivery:** POST to the subscriber's configured URL.
- **Timeout:** 5 seconds per request.
- **Retry:** Up to 5 times with exponential backoff (1min, 5min, 15min, 1hr, 6hr).
- **Dead letter:** After 5 failed attempts, event is stored in dead letter queue for manual retry.
- **Signature:** HMAC-SHA256 with shared secret in header: `X-Webhook-Signature`.
- **Idempotency:** Events include `eventId` — subscribers should deduplicate by this ID.

---

## 10. SDK / Client Library Documentation

### SDK Principles

- **Auto-generated:** SDKs are generated from OpenAPI specification.
- **Typed:** Full TypeScript type definitions.
- **Idempotent:** Retry logic and idempotency keys are handled automatically.
- **Observable:** Every request logs duration and status.

### SDK Usage Example (TypeScript)

```typescript
import { APIClient } from '@project/api-client';

const client = new APIClient({
  baseUrl: 'https://api.example.com/v1',
  accessToken: 'eyJhbGciOiJSUzI1NiIs...',  // optional - can also use login()
});

// Login
const { user, accessToken } = await client.auth.login({
  email: 'user@example.com',
  password: 'ValidP@ss123',
});

// List products (with typing)
const { data: products, meta } = await client.products.list({
  page: 1,
  pageSize: 20,
  category: 'electronics',
  sortBy: 'price',
  sortOrder: 'asc',
});

// Create order (with idempotency)
const { data: order } = await client.orders.create(
  {
    shippingAddressId: 'uuid-addr-001',
    items: [{ productId: 'uuid-prod-001', quantity: 1 }],
  },
  {
    idempotencyKey: 'unique-key-for-retry',
  },
);

// Error handling (typed errors)
try {
  await client.products.create(productData);
} catch (error) {
  if (error instanceof ApiError) {
    if (error.code === 'VALIDATION_ERROR') {
      console.error('Validation failed:', error.details);
    } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
      console.error('Rate limited, retry after:', error.retryAfter);
    }
  }
}

// Webhook verification
const isValid = client.webhooks.verifySignature(
  rawBody,
  signatureHeader,
  sharedSecret,
);
```

---

## Appendix A: Endpoint Index

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/auth/register | No | Register new user |
| POST | /api/v1/auth/login | No | Login |
| POST | /api/v1/auth/refresh | Refresh token | Refresh tokens |
| POST | /api/v1/auth/logout | Yes | Logout |
| POST | /api/v1/auth/oauth | No | OAuth login |
| GET | /api/v1/users/me | Yes | Get profile |
| PATCH | /api/v1/users/me | Yes | Update profile |
| DELETE | /api/v1/users/me | Yes | Delete account |
| GET | /api/v1/products | No | List products |
| GET | /api/v1/products/:id | No | Get product |
| POST | /api/v1/products | Admin | Create product |
| PATCH | /api/v1/products/:id | Admin | Update product |
| DELETE | /api/v1/products/:id | Admin | Delete product |
| POST | /api/v1/orders | Yes | Create order |
| GET | /api/v1/orders | Yes | List orders |
| GET | /api/v1/orders/:id | Yes | Get order |
| POST | /api/v1/orders/:id/cancel | Yes | Cancel order |
| GET | /api/v1/cart | Yes | Get cart |
| POST | /api/v1/cart/items | Yes | Add to cart |
| PATCH | /api/v1/cart/items/:itemId | Yes | Update cart item |
| DELETE | /api/v1/cart/items/:itemId | Yes | Remove from cart |
| POST | /api/v1/payments/intent | Yes | Create payment intent |
| POST | /api/v1/webhooks/payments | HMAC | Payment webhook |
| POST | /api/v1/webhooks/email | HMAC | Email webhook |

## Appendix B: OpenAPI Specification

The full OpenAPI 3.1 specification is maintained in `api/openapi.yaml` and is the authoritative source of truth for all endpoints. This document is a human-readable summary.

## Appendix C: Change Log

| Date | Author | Change | Rationale |
|---|---|---|---|
| [DATE] | [AUTHOR] | Initial creation | API documentation baseline |
| [DATE] | [AUTHOR] | [CHANGE] | [RATIONALE] |

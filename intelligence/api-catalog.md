# API Catalog

## Auth Endpoints

### POST /auth/register
- **Purpose**: Create a new user account.
- **Auth**: None (public endpoint).
- **Rate Limit**: 3 requests per minute per IP.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Str0ng!Pass",
    "name": "Jane Doe"
  }
  ```
- **Validation**: BR-001 (email unique), BR-002 (password strength), email format, name length 1-100.
- **Success Response** (201):
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "Jane Doe",
    "role": "buyer",
    "emailVerified": false,
    "createdAt": "2025-01-01T00:00:00Z"
  }
  ```
- **Error Responses**:
  - 409: Email already exists
  - 422: Validation failed (detailed field errors)
  - 429: Rate limit exceeded
- **Idempotent**: No (creates new resource each time).

### POST /auth/login
- **Purpose**: Authenticate user and return tokens.
- **Auth**: None (public endpoint).
- **Rate Limit**: 10 requests per minute per IP.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Str0ng!Pass"
  }
  ```
- **Validation**: Email and password required.
- **Success Response** (200):
  ```json
  {
    "accessToken": "jwt...",
    "refreshToken": "jwt...",
    "expiresIn": 900,
    "user": { "id": "uuid", "email": "...", "name": "...", "role": "buyer" }
  }
  ```
- **Error Responses**:
  - 401: Invalid credentials
  - 423: Account locked (includes Retry-After header)
  - 422: Validation failed
- **Idempotent**: Yes (no state change on read).

### POST /auth/refresh
- **Purpose**: Refresh an expired access token.
- **Auth**: Refresh token (in request body).
- **Rate Limit**: 5 requests per minute per user.
- **Request Body**:
  ```json
  { "refreshToken": "jwt..." }
  ```
- **Success Response** (200):
  ```json
  {
    "accessToken": "jwt...",
    "refreshToken": "jwt...",
    "expiresIn": 900
  }
  ```
- **Error Responses**:
  - 401: Invalid or expired refresh token
  - 400: Refresh token rotation detected (possible token theft)
- **Idempotent**: No (token rotation invalidates old token).

### POST /auth/logout
- **Purpose**: Invalidate the current refresh token family.
- **Auth**: Access token (Bearer header).
- **Request Body**:
  ```json
  { "refreshToken": "jwt..." }
  ```
- **Success Response** (200): `{ "message": "Logged out" }`
- **Idempotent**: Yes.

## Product Endpoints

### GET /products
- **Purpose**: List products with filtering and pagination.
- **Auth**: None (public endpoint).
- **Query Parameters**: `page` (default 1), `limit` (default 20, max 100), `category`, `minPrice`, `maxPrice`, `sortBy` (price, name, newest), `sortOrder` (asc, desc), `search`.
- **Cache**: 5 minutes (CDN + Redis).
- **Success Response** (200):
  ```json
  {
    "data": [{ "id": "uuid", "name": "...", "slug": "...", "listPrice": 1999, "salePrice": null, "imageUrl": "...", "category": "..." }],
    "pagination": { "page": 1, "limit": 20, "total": 350, "totalPages": 18 }
  }
  ```
- **Error Responses**:
  - 422: Invalid query parameters.
- **Idempotent**: Yes (read-only).

### GET /products/:slug
- **Purpose**: Get product details by slug.
- **Auth**: None (public endpoint).
- **Cache**: 5 minutes (CDN + Redis).
- **Success Response** (200):
  ```json
  {
    "id": "uuid",
    "name": "...",
    "slug": "...",
    "description": "...",
    "listPrice": 1999,
    "salePrice": 1499,
    "category": { "id": "uuid", "name": "..." },
    "variants": [{ "id": "uuid", "sku": "XXX-001", "attributes": { "color": "red", "size": "M" }, "inventory": { "available": 42 } }],
    "reviews": { "averageRating": 4.5, "count": 128 }
  }
  ```
- **Error Responses**:
  - 404: Product not found.
  - 410: Product deleted.
- **Idempotent**: Yes.

### GET /products/search
- **Purpose**: Full-text search across products.
- **Auth**: None (public endpoint).
- **Query Parameters**: `q` (search query, required), `page`, `limit`.
- **Cache**: 1 minute (CDN).
- **Success Response** (200): Same shape as GET /products.
- **Error Responses**:
  - 422: Missing search query.
- **Idempotent**: Yes.

### POST /products
- **Purpose**: Create a new product (seller only).
- **Auth**: Access token (seller role required).
- **Request Body**:
  ```json
  {
    "name": "...",
    "description": "...",
    "categoryId": "uuid",
    "variants": [{ "sku": "XXX-001", "attributes": {}, "listPrice": 1999, "costPrice": 1000, "quantity": 100 }]
  }
  ```
- **Success Response** (201): Full product object.
- **Error Responses**:
  - 401: Not authenticated.
  - 403: Not a seller.
  - 409: SKU already exists.
  - 422: Validation failed.
- **Idempotent**: No.

## Cart Endpoints

### GET /cart
- **Purpose**: Get the current user's cart with items and totals.
- **Auth**: Access token (Bearer header).
- **Success Response** (200):
  ```json
  {
    "id": "uuid",
    "items": [{ "id": "uuid", "variantId": "uuid", "productName": "...", "quantity": 2, "unitPrice": 1999, "lineTotal": 3998 }],
    "subtotal": 3998,
    "itemCount": 2
  }
  ```
- **Idempotent**: Yes.

### POST /cart/items
- **Purpose**: Add an item to the cart.
- **Auth**: Access token (Bearer header).
- **Request Body**:
  ```json
  { "variantId": "uuid", "quantity": 1 }
  ```
- **Validation**: Quantity >= 1, variant must exist and be active.
- **Success Response** (201): Updated cart object.
- **Error Responses**:
  - 404: Variant not found.
  - 422: Invalid quantity.
- **Idempotent**: No.

### PUT /cart/items/:id
- **Purpose**: Update item quantity in the cart.
- **Auth**: Access token (Bearer header).
- **Request Body**:
  ```json
  { "quantity": 3 }
  ```
- **Success Response** (200): Updated cart object.
- **Idempotent**: Yes (setting same quantity is idempotent).

### DELETE /cart/items/:id
- **Purpose**: Remove an item from the cart.
- **Auth**: Access token (Bearer header).
- **Success Response** (200): Updated cart object.
- **Idempotent**: Yes (deleting already deleted item returns success).

## Order Endpoints

### GET /orders
- **Purpose**: List current user's orders.
- **Auth**: Access token (Bearer header).
- **Query Parameters**: `page`, `limit`, `status`.
- **Success Response** (200): Paginated order list.
- **Idempotent**: Yes.

### GET /orders/:id
- **Purpose**: Get order details.
- **Auth**: Access token (order owner or admin).
- **Success Response** (200): Full order object with items, payment, shipment.
- **Error Responses**:
  - 403: Not authorized.
  - 404: Order not found.
- **Idempotent**: Yes.

### POST /orders/:id/cancel
- **Purpose**: Cancel an order.
- **Auth**: Access token (order owner or admin).
- **Success Response** (200): Updated order with "cancelled" status.
- **Error Responses**:
  - 400: Order cannot be cancelled (wrong status).
  - 403: Not authorized.
  - 404: Order not found.
- **Idempotent**: Yes (cancelling already-cancelled order returns success).

### POST /checkout
- **Purpose**: Place an order from the current cart.
- **Auth**: Access token (Bearer header).
- **Rate Limit**: 3 requests per minute per user.
- **Request Body**:
  ```json
  {
    "shippingAddressId": "uuid",
    "shippingMethod": "standard",
    "paymentMethod": "card",
    "discountCode": "SAVE20",
    "notes": "Leave at the door"
  }
  ```
- **Success Response** (201): Order object.
- **Error Responses**:
  - 400: Cart is empty.
  - 409: Inventory insufficient.
  - 422: Validation failed.
- **Idempotent**: Yes (via idempotency key header).

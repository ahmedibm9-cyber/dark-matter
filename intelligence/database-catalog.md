# Database Catalog

## Schema: public

## Tables

### users
- **Purpose**: Stores registered user accounts and profiles.
- **Columns**:
  | Column | Type | Constraints | Notes |
  |--------|------|-------------|-------|
  | id | UUID | PK, DEFAULT gen_random_uuid() | |
  | email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Lowercase enforced via trigger |
  | password_hash | VARCHAR(255) | NOT NULL | bcrypt hash, cost 12 |
  | name | VARCHAR(100) | NOT NULL | |
  | role | VARCHAR(20) | NOT NULL, DEFAULT 'buyer' | Enum: buyer, seller, admin |
  | email_verified | BOOLEAN | NOT NULL, DEFAULT false | |
  | avatar_url | VARCHAR(500) | NULLABLE | |
  | phone | VARCHAR(20) | NULLABLE | |
  | deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete (FAIL-002) |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Auto-updated via trigger |
- **Indexes**:
  - `idx_users_email` on email (UNIQUE)
  - `idx_users_role` on role
  - `idx_users_deleted_at` on deleted_at (partial index WHERE deleted_at IS NULL)
- **Relationships**: Has many orders, products, reviews, addresses, cart.

### refresh_tokens
- **Purpose**: Stores refresh token hashes for token rotation.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | user_id | UUID | FK -> users.id, NOT NULL, INDEX |
  | token_hash | VARCHAR(255) | NOT NULL, UNIQUE |
  | family | VARCHAR(100) | NOT NULL, INDEX |
  | expires_at | TIMESTAMPTZ | NOT NULL |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_refresh_tokens_user_id` on user_id
  - `idx_refresh_tokens_family` on family
  - `idx_refresh_tokens_expires_at` on expires_at
- **Relationships**: Belongs to user.

### categories
- **Purpose**: Product category hierarchy.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | name | VARCHAR(100) | NOT NULL |
  | slug | VARCHAR(150) | UNIQUE, NOT NULL, INDEX |
  | description | TEXT | NULLABLE |
  | parent_id | UUID | FK -> categories.id, NULLABLE, INDEX |
  | sort_order | INTEGER | NOT NULL, DEFAULT 0 |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_categories_slug` on slug (UNIQUE)
  - `idx_categories_parent_id` on parent_id
- **Relationships**: Self-referential (parent_id), has many products.

### products
- **Purpose**: Product listings managed by sellers.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | seller_id | UUID | FK -> users.id, NOT NULL, INDEX |
  | category_id | UUID | FK -> categories.id, NOT NULL, INDEX |
  | name | VARCHAR(200) | NOT NULL |
  | slug | VARCHAR(250) | UNIQUE, NOT NULL |
  | description | TEXT | NOT NULL |
  | status | VARCHAR(20) | NOT NULL, DEFAULT 'active' |
  | deleted_at | TIMESTAMPTZ | NULLABLE |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_products_seller_id` on seller_id
  - `idx_products_category_id` on category_id
  - `idx_products_slug` on slug (UNIQUE)
  - `idx_products_status` on status
- **Relationships**: Belongs to seller (user), belongs to category, has many variants, has many reviews.

### variants
- **Purpose**: Product variants (size, color, etc.).
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | product_id | UUID | FK -> products.id, NOT NULL, INDEX |
  | sku | VARCHAR(20) | UNIQUE, NOT NULL |
  | attributes | JSONB | NOT NULL, DEFAULT '{}' |
  | list_price | INTEGER | NOT NULL | In cents |
  | cost_price | INTEGER | NOT NULL | In cents |
  | sale_price | INTEGER | NULLABLE | In cents |
  | status | VARCHAR(20) | NOT NULL, DEFAULT 'active' |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_variants_product_id` on product_id
  - `idx_variants_sku` on sku (UNIQUE)
  - `idx_variants_attributes` GIN index on attributes
- **Relationships**: Belongs to product, has one inventory, has many order_items, has many cart_items.

### inventory
- **Purpose**: Stock tracking per variant.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | variant_id | UUID | FK -> variants.id, UNIQUE, NOT NULL |
  | quantity | INTEGER | NOT NULL, DEFAULT 0 |
  | reserved_quantity | INTEGER | NOT NULL, DEFAULT 0 |
  | low_stock_threshold | INTEGER | NOT NULL, DEFAULT 10 |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Check Constraints**:
  - `ck_inventory_quantity` CHECK (quantity >= 0)
  - `ck_inventory_reserved` CHECK (reserved_quantity >= 0)
  - `ck_inventory_reserved_not_exceed` CHECK (reserved_quantity <= quantity)
- **Relationships**: Belongs to variant.

### carts
- **Purpose**: Shopping carts for users.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | user_id | UUID | FK -> users.id, UNIQUE, NOT NULL |
  | expires_at | TIMESTAMPTZ | NOT NULL |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_carts_user_id` on user_id (UNIQUE)
  - `idx_carts_expires_at` on expires_at
- **Relationships**: Belongs to user, has many cart_items.

### cart_items
- **Purpose**: Line items within a cart.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | cart_id | UUID | FK -> carts.id, NOT NULL, INDEX |
  | variant_id | UUID | FK -> variants.id, NOT NULL |
  | quantity | INTEGER | NOT NULL, CHECK (quantity > 0) |
  | unit_price | INTEGER | NOT NULL |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**: `idx_cart_items_cart_id` on cart_id
- **Relationships**: Belongs to cart, belongs to variant.

### orders
- **Purpose**: Customer orders with full lifecycle.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | user_id | UUID | FK -> users.id, NOT NULL, INDEX |
  | order_number | VARCHAR(20) | UNIQUE, NOT NULL |
  | status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
  | subtotal | INTEGER | NOT NULL | In cents |
  | tax_total | INTEGER | NOT NULL | In cents |
  | shipping_total | INTEGER | NOT NULL | In cents |
  | grand_total | INTEGER | NOT NULL | In cents |
  | currency | VARCHAR(3) | NOT NULL, DEFAULT 'USD' |
  | discount_id | UUID | FK -> discounts.id, NULLABLE |
  | notes | TEXT | NULLABLE |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_orders_user_id` on user_id
  - `idx_orders_status` on status
  - `idx_orders_order_number` on order_number (UNIQUE)
  - `idx_orders_created_at` on created_at
- **Relationships**: Belongs to user, has many order_items, has one payment, has one shipment, has many status_histories.

### order_items
- **Purpose**: Line items within an order.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | order_id | UUID | FK -> orders.id, NOT NULL, INDEX |
  | variant_id | UUID | FK -> variants.id, NOT NULL |
  | product_snapshot | JSONB | NOT NULL |
  | quantity | INTEGER | NOT NULL, CHECK (quantity > 0) |
  | unit_price | INTEGER | NOT NULL |
  | line_total | INTEGER | NOT NULL |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**: `idx_order_items_order_id` on order_id
- **Relationships**: Belongs to order, belongs to variant.

### payments
- **Purpose**: Payment transactions for orders.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | order_id | UUID | FK -> orders.id, UNIQUE, NOT NULL |
  | method | VARCHAR(20) | NOT NULL |
  | status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
  | amount | INTEGER | NOT NULL |
  | currency | VARCHAR(3) | NOT NULL, DEFAULT 'USD' |
  | transaction_id | VARCHAR(255) | NULLABLE |
  | gateway_response | JSONB | NULLABLE |
  | idempotency_key | VARCHAR(255) | UNIQUE, NULLABLE |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_payments_order_id` on order_id (UNIQUE)
  - `idx_payments_idempotency_key` on idempotency_key (UNIQUE)
- **Relationships**: Belongs to order.

### shipments
- **Purpose**: Shipping details for orders.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | order_id | UUID | FK -> orders.id, UNIQUE, NOT NULL |
  | address_snapshot | JSONB | NOT NULL |
  | method | VARCHAR(50) | NOT NULL |
  | carrier | VARCHAR(100) | NULLABLE |
  | tracking_number | VARCHAR(100) | NULLABLE, INDEX |
  | status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
  | estimated_delivery | DATE | NULLABLE |
  | shipped_at | TIMESTAMPTZ | NULLABLE |
  | delivered_at | TIMESTAMPTZ | NULLABLE |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
  | updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_shipments_order_id` on order_id (UNIQUE)
  - `idx_shipments_tracking_number` on tracking_number
- **Relationships**: Belongs to order.

### discounts
- **Purpose**: Discount/coupon codes.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | code | VARCHAR(50) | UNIQUE, NOT NULL |
  | type | VARCHAR(20) | NOT NULL | percentage or fixed |
  | value | INTEGER | NOT NULL | Percentage points or cents |
  | min_order_amount | INTEGER | NULLABLE |
  | max_usage_count | INTEGER | NULLABLE |
  | current_usage_count | INTEGER | NOT NULL, DEFAULT 0 |
  | expires_at | TIMESTAMPTZ | NOT NULL |
  | is_active | BOOLEAN | NOT NULL, DEFAULT true |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**: `idx_discounts_code` on code (UNIQUE)
- **Relationships**: Has many orders.

### reviews
- **Purpose**: Product reviews from buyers.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | product_id | UUID | FK -> products.id, NOT NULL, INDEX |
  | user_id | UUID | FK -> users.id, NOT NULL |
  | rating | SMALLINT | NOT NULL, CHECK (1-5) |
  | title | VARCHAR(200) | NULLABLE |
  | body | TEXT | NULLABLE |
  | is_verified_purchase | BOOLEAN | NOT NULL, DEFAULT false |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_reviews_product_id` on product_id
- **Relationships**: Belongs to product, belongs to user.

### addresses
- **Purpose**: User shipping/billing addresses.
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | user_id | UUID | FK -> users.id, NOT NULL, INDEX |
  | label | VARCHAR(50) | NOT NULL |
  | first_name | VARCHAR(100) | NOT NULL |
  | last_name | VARCHAR(100) | NOT NULL |
  | line1 | VARCHAR(255) | NOT NULL |
  | line2 | VARCHAR(255) | NULLABLE |
  | city | VARCHAR(100) | NOT NULL |
  | state | VARCHAR(100) | NOT NULL |
  | postal_code | VARCHAR(20) | NOT NULL |
  | country | VARCHAR(3) | NOT NULL |
  | is_default | BOOLEAN | NOT NULL, DEFAULT false |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**: `idx_addresses_user_id` on user_id
- **Relationships**: Belongs to user.

### audit_logs
- **Purpose**: Compliance audit trail (BR-021).
- **Columns**:
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | UUID | PK |
  | entity_type | VARCHAR(50) | NOT NULL, INDEX |
  | entity_id | UUID | NOT NULL, INDEX |
  | action | VARCHAR(50) | NOT NULL |
  | actor_id | UUID | FK -> users.id, NOT NULL, INDEX |
  | before_state | JSONB | NULLABLE |
  | after_state | JSONB | NULLABLE |
  | ip_address | INET | NULLABLE |
  | user_agent | TEXT | NULLABLE |
  | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Indexes**:
  - `idx_audit_logs_entity` on (entity_type, entity_id)
  - `idx_audit_logs_actor_id` on actor_id
  - `idx_audit_logs_created_at` on created_at

## Materialized Views

### product_search_mview
- **Purpose**: Denormalized product search index for full-text search.
- **Refresh**: Every 5 minutes via cron job.
- **Columns**: product_id, name, description, category_name, seller_name, variants_count, avg_rating, review_count, search_vector (tsvector).

## Functions

### update_updated_at_column()
- **Purpose**: Auto-update updated_at column on row modification.
- **Trigger On**: All tables with updated_at column.
- **Behavior**: Sets updated_at = NOW() on UPDATE.

### lower_email_trigger()
- **Purpose**: Enforce lowercase email on insert/update.
- **Trigger On**: users table.
- **Behavior**: Sets NEW.email = LOWER(NEW.email).

## Notes
- All monetary values stored as INTEGER (cents) to avoid floating-point issues (BR-013).
- Soft delete pattern (FAIL-002): deleted_at column, queries default to WHERE deleted_at IS NULL.
- Audit log retention: 7 years (BR-022).

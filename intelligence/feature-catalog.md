# Feature Catalog

## F-001: User Registration
- **Purpose**: Allow new users to create an account on the platform.
- **Source Files**:
  - `apps/web/app/(auth)/register/page.tsx` — Registration form UI
  - `apps/web/app/(auth)/register/actions.ts` — Server actions
  - `services/api/src/modules/auth/register.handler.ts` — Registration handler
  - `services/api/src/modules/auth/register.schema.ts` — Zod schema
  - `services/api/src/modules/auth/register.service.ts` — Business logic
- **APIs**: POST /auth/register
- **DB Objects**: users table, email_verification_tokens table
- **Dependencies**: Email service (transactional), Redis (rate limiting)
- **Tests**:
  - `apps/web/__tests__/register/page.test.tsx` — UI tests
  - `services/api/__tests__/auth/register.test.ts` — API tests
  - `services/api/__tests__/auth/register.integration.test.ts` — Integration tests
- **Business Rules**: BR-001, BR-002, BR-005
- **Last Verified**: Not yet

## F-002: User Login
- **Purpose**: Authenticate existing users and issue session tokens.
- **Source Files**:
  - `apps/web/app/(auth)/login/page.tsx` — Login form UI
  - `apps/web/app/(auth)/login/actions.ts` — Server actions
  - `services/auth/src/modules/auth/login.handler.ts` — Login handler
  - `services/auth/src/modules/auth/login.schema.ts` — Zod schema
  - `services/auth/src/modules/auth/login.service.ts` — Business logic
  - `services/auth/src/modules/auth/token.service.ts` — Token generation
- **APIs**: POST /auth/login
- **DB Objects**: users table, refresh_tokens table
- **Dependencies**: Redis (rate limiting, session cache)
- **Tests**:
  - `apps/web/__tests__/login/page.test.tsx` — UI tests
  - `services/auth/__tests__/login.test.ts` — API tests
  - `services/auth/__tests__/token.test.ts` — Token tests
- **Business Rules**: BR-003, BR-004
- **Last Verified**: Not yet

## F-003: Product Browsing
- **Purpose**: Allow users to browse, search, and filter products.
- **Source Files**:
  - `apps/web/app/products/page.tsx` — Product listing page
  - `apps/web/app/products/[slug]/page.tsx` — Product detail page
  - `apps/web/components/products/ProductCard.tsx` — Product card component
  - `apps/web/components/products/ProductFilter.tsx` — Filter component
  - `apps/web/components/products/ProductGrid.tsx` — Grid layout
  - `services/api/src/modules/products/list.handler.ts` — List products handler
  - `services/api/src/modules/products/detail.handler.ts` — Product detail handler
  - `services/api/src/modules/products/search.service.ts` — Search logic
- **APIs**: GET /products, GET /products/:slug, GET /products/search
- **DB Objects**: products table, variants table, categories table, product_search MVIEW
- **Dependencies**: Search index service, Redis cache (product cache)
- **Tests**:
  - `apps/web/__tests__/products/listing.test.tsx`
  - `apps/web/__tests__/products/detail.test.tsx`
  - `services/api/__tests__/products/list.test.ts`
  - `services/api/__tests__/products/search.test.ts`
- **Business Rules**: BR-014
- **Last Verified**: Not yet

## F-004: Shopping Cart
- **Purpose**: Allow users to manage items they intend to purchase.
- **Source Files**:
  - `apps/web/app/cart/page.tsx` — Cart page
  - `apps/web/components/cart/CartItem.tsx` — Cart item component
  - `apps/web/components/cart/CartSummary.tsx` — Cart summary component
  - `apps/web/hooks/useCart.ts` — Cart state management
  - `services/api/src/modules/cart/cart.handler.ts` — Cart CRUD handler
  - `services/api/src/modules/cart/cart.service.ts` — Cart business logic
  - `services/api/src/modules/cart/cart.schema.ts` — Cart validation
- **APIs**: GET /cart, POST /cart/items, PUT /cart/items/:id, DELETE /cart/items/:id
- **DB Objects**: carts table, cart_items table
- **Dependencies**: Redis (cart expiry tracking)
- **Tests**:
  - `apps/web/__tests__/cart/page.test.tsx`
  - `apps/web/__tests__/cart/cart-item.test.tsx`
  - `services/api/__tests__/cart/cart.test.ts`
- **Business Rules**: None specific
- **Last Verified**: Not yet

## F-005: Checkout
- **Purpose**: Complete the purchase process with address, shipping, and payment.
- **Source Files**:
  - `apps/web/app/checkout/page.tsx` — Checkout page
  - `apps/web/app/checkout/AddressForm.tsx` — Address input
  - `apps/web/app/checkout/PaymentForm.tsx` — Payment input
  - `apps/web/app/checkout/ReviewOrder.tsx` — Order review
  - `services/api/src/modules/checkout/checkout.handler.ts` — Checkout handler
  - `services/api/src/modules/checkout/checkout.service.ts` — Checkout business logic
  - `services/api/src/modules/checkout/checkout.schema.ts` — Validation
  - `services/api/src/modules/checkout/shipping.service.ts` — Shipping calculation
  - `services/api/src/modules/checkout/discount.service.ts` — Discount application
- **APIs**: POST /checkout, GET /checkout/shipping-rates, POST /checkout/validate-discount
- **DB Objects**: orders table, order_items table, payments table, shipments table
- **Dependencies**: Payment gateway, Redis (inventory reservation), BullMQ (async processing)
- **Tests**:
  - `apps/web/__tests__/checkout/flow.test.tsx`
  - `services/api/__tests__/checkout/checkout.test.ts`
  - `services/api/__tests__/checkout/shipping.test.ts`
  - `services/api/__tests__/checkout/discount.test.ts`
  - `services/api/__tests__/checkout/checkout.integration.test.ts`
- **Business Rules**: BR-007, BR-008, BR-009, BR-010, BR-015, BR-016, BR-017, BR-018, BR-019
- **Last Verified**: Not yet

## F-006: Order Management
- **Purpose**: Allow users and admins to view and manage orders.
- **Source Files**:
  - `apps/web/app/account/orders/page.tsx` — User order history
  - `apps/web/app/account/orders/[id]/page.tsx` — Order detail
  - `apps/web/app/admin/orders/page.tsx` — Admin order list
  - `apps/web/app/admin/orders/[id]/page.tsx` — Admin order detail
  - `services/api/src/modules/orders/list.handler.ts` — Order list
  - `services/api/src/modules/orders/detail.handler.ts` — Order detail
  - `services/api/src/modules/orders/cancel.handler.ts` — Order cancellation
- **APIs**: GET /orders, GET /orders/:id, POST /orders/:id/cancel
- **DB Objects**: orders table, order_items table, order_status_history table
- **Dependencies**: None
- **Tests**:
  - `apps/web/__tests__/orders/history.test.tsx`
  - `apps/web/__tests__/orders/detail.test.tsx`
  - `services/api/__tests__/orders/list.test.ts`
  - `services/api/__tests__/orders/cancel.test.ts`
- **Business Rules**: BR-010, BR-011
- **Last Verified**: Not yet

## F-007: Admin Dashboard
- **Purpose**: Provide administrators with platform overview and management tools.
- **Source Files**:
  - `apps/web/app/admin/page.tsx` — Dashboard
  - `apps/web/app/admin/users/page.tsx` — User management
  - `apps/web/app/admin/products/page.tsx` — Product management
  - `apps/web/app/admin/discounts/page.tsx` — Discount management
  - `services/api/src/modules/admin/dashboard.handler.ts`
  - `services/api/src/modules/admin/users.handler.ts`
  - `services/api/src/modules/admin/products.handler.ts`
  - `services/api/src/modules/admin/discounts.handler.ts`
- **APIs**: GET /admin/dashboard, GET /admin/users, PUT /admin/users/:id, GET /admin/products, PUT /admin/products/:id
- **DB Objects**: All tables (admin has full access)
- **Dependencies**: All services
- **Tests**: Minimal coverage (admin features are low priority for automated testing)
- **Business Rules**: BR-006, BR-021
- **Last Verified**: Not yet

# Knowledge Graph — Project Entity Relationship Map

> **Purpose:** Map all relationships between entities in the project.  
> **Last Updated:** 2026-06-25  
> **Owner:** Project Lead

---

## 1. Entity-Relationship Map

### 1.1 Features → Modules

| Feature ID | Feature Name | Implemented In | Status |
|---|---|---|---|
| F-001 | User Authentication | `services/auth/` | Active |
| F-002 | User Registration | `services/auth/`, `services/email/` | Active |
| F-003 | User Profile Management | `services/auth/`, `apps/web/` | Active |
| F-004 | Password Reset | `services/auth/`, `services/email/` | Active |
| F-005 | Multi-tenant Organization Management | `services/org/`, `apps/web/admin/` | Active |
| F-006 | Role-based Access Control (RBAC) | `services/auth/`, `middleware/rbac.ts` | Active |
| F-007 | Product Catalog | `services/catalog/`, `apps/web/products/` | Active |
| F-008 | Shopping Cart | `services/cart/`, `apps/web/cart/` | Active |
| F-009 | Checkout & Payment | `services/orders/`, `services/billing/` | Active |
| F-010 | Order Management | `services/orders/`, `apps/web/orders/` | Active |
| F-011 | Subscription Management | `services/billing/`, `services/email/` | Active |
| F-012 | Report Generation | `services/reports/`, `apps/web/reports/` | Active |
| F-013 | File Upload & Management | `services/storage/`, `apps/web/files/` | Active |
| F-014 | Search | `services/search/`, `apps/web/search/` | Beta |
| F-015 | Notification System | `services/notifications/`, `services/email/` | Active |
| F-016 | Audit Logging | `services/audit/` | Active |
| F-017 | API Key Management | `services/auth/`, `apps/web/settings/` | Active |
| F-018 | Webhook System | `services/webhooks/` | Active |
| F-019 | Data Export | `services/reports/` | Active |
| F-020 | Team Collaboration | `services/collab/` | Planned |
| F-101 | Legacy v1 API | `legacy/` | Deprecated |

### 1.2 Modules → Files

| Module | Files | Description |
|---|---|---|
| `services/auth/` | `src/authController.ts` | HTTP route handlers for auth endpoints |
| `services/auth/` | `src/authService.ts` | Core authentication business logic |
| `services/auth/` | `src/userRepository.ts` | User data access layer |
| `services/auth/` | `src/validation.ts` | Input validation schemas |
| `services/auth/` | `src/session.ts` | Session management |
| `services/auth/` | `src/rules/concurrent.ts` | Concurrent login rules |
| `services/auth/` | `src/rbac.ts` | Role/permission checks |
| `services/auth/` | `src/middleware/requireAuth.ts` | Auth middleware |
| `services/email/` | `src/emailService.ts` | Email sending logic |
| `services/email/` | `src/emailQueue.ts` | Async email job queue |
| `services/email/` | `src/templates/` | Email template rendering |
| `services/email/` | `src/providers/sendgrid.ts` | SendGrid provider integration |
| `services/email/` | `src/providers/ses.ts` | AWS SES provider integration |
| `services/billing/` | `src/paymentService.ts` | Payment processing |
| `services/billing/` | `src/subscriptionService.ts` | Subscription lifecycle |
| `services/billing/` | `src/invoiceService.ts` | Invoice generation |
| `services/billing/` | `src/rules/trial.ts` | Trial period business rules |
| `services/billing/` | `src/rules/discounts.ts` | Discount calculation rules |
| `services/billing/` | `src/rules/refunds.ts` | Refund policy rules |
| `services/billing/` | `src/gateways/stripe.ts` | Stripe integration |
| `services/billing/` | `src/gateways/paypal.ts` | PayPal integration |
| `services/orders/` | `src/orderService.ts` | Order management logic |
| `services/orders/` | `src/orderRepository.ts` | Order data access |
| `services/orders/` | `src/rules/cancellation.ts` | Cancellation window rules |
| `services/orders/` | `src/shippingService.ts` | Shipping calculation |
| `services/catalog/` | `src/productService.ts` | Product CRUD operations |
| `services/catalog/` | `src/productRepository.ts` | Product data access |
| `services/catalog/` | `src/categoryService.ts` | Category management |
| `services/catalog/` | `src/searchService.ts` | Product search (internal) |
| `services/cart/` | `src/cartService.ts` | Cart management logic |
| `services/cart/` | `src/cartRepository.ts` | Cart data access |
| `services/org/` | `src/orgService.ts` | Organization management |
| `services/org/` | `src/orgRepository.ts` | Organization data access |
| `services/org/` | `src/teamService.ts` | Team management |
| `services/org/` | `src/invitationService.ts` | Invitation flow |
| `services/reports/` | `src/reportService.ts` | Report generation logic |
| `services/reports/` | `src/queryBuilder.ts` | Dynamic query construction |
| `services/reports/` | `src/export.ts` | Export logic (CSV/PDF) |
| `services/reports/` | `src/scheduler.ts` | Scheduled report delivery |
| `services/storage/` | `src/fileService.ts` | File management |
| `services/storage/` | `src/storageProvider.ts` | Storage abstraction layer |
| `services/storage/` | `src/providers/s3.ts` | AWS S3 provider |
| `services/storage/` | `src/providers/local.ts` | Local filesystem provider |
| `services/notifications/` | `src/notificationService.ts` | Notification dispatch |
| `services/notifications/` | `src/channels/email.ts` | Email notification channel |
| `services/notifications/` | `src/channels/slack.ts` | Slack notification channel |
| `services/notifications/` | `src/channels/push.ts` | Push notification channel |
| `services/notifications/` | `src/preferencesService.ts` | User notification preferences |
| `services/audit/` | `src/auditService.ts` | Audit event logging |
| `services/audit/` | `src/auditRepository.ts` | Audit data access |
| `services/audit/` | `src/eventTypes.ts` | Audit event type definitions |
| `services/search/` | `src/searchService.ts` | Full-text search logic |
| `services/search/` | `src/indexService.ts` | Search index management |
| `services/search/` | `src/cache.ts` | Search result caching |
| `services/webhooks/` | `src/webhookService.ts` | Webhook dispatch |
| `services/webhooks/` | `src/webhookRepository.ts` | Webhook config data access |
| `services/webhooks/` | `src/deliveryService.ts` | Webhook delivery with retry |
| `apps/web/` | `src/pages/` | Route pages |
| `apps/web/` | `src/components/` | Shared UI components |
| `apps/web/` | `src/hooks/` | Custom React hooks |
| `apps/web/` | `src/api/` | API client wrappers |
| `apps/web/` | `src/store/` | State management |
| `middleware/` | `rateLimiter.ts` | Rate limiting middleware |
| `middleware/` | `errorHandler.ts` | Global error handler |
| `middleware/` | `requestLogger.ts` | Request logging middleware |
| `middleware/` | `rbac.ts` | Role-based access middleware |
| `middleware/` | `requireAuth.ts` | Authentication guard |

### 1.3 Services → Database Tables

| Service | Tables Used | Access Pattern |
|---|---|---|
| `services/auth/` | `users`, `sessions`, `roles`, `permissions`, `api_keys` | Read/Write |
| `services/email/` | `email_queue`, `email_logs`, `email_templates` | Read/Write |
| `services/billing/` | `subscriptions`, `invoices`, `payments`, `plans`, `discounts` | Read/Write |
| `services/orders/` | `orders`, `order_items`, `shipments`, `cancellations` | Read/Write |
| `services/catalog/` | `products`, `categories`, `product_variants`, `inventory` | Read/Write |
| `services/cart/` | `carts`, `cart_items` | Read/Write |
| `services/org/` | `organizations`, `teams`, `team_members`, `invitations` | Read/Write |
| `services/reports/` | `reports`, `report_schedules`, `export_logs` | Read/Write |
| `services/storage/` | `files`, `file_versions`, `storage_quotas` | Read/Write |
| `services/notifications/` | `notifications`, `notification_preferences`, `notification_logs` | Read/Write |
| `services/audit/` | `audit_events`, `audit_event_details` | Write-heavy |
| `services/search/` | `search_index`, `search_synonyms` | Read/Write |
| `services/webhooks/` | `webhook_configs`, `webhook_deliveries` | Read/Write |

### 1.4 API Endpoints → Services

| Endpoint | Method | Service | Description |
|---|---|---|---|
| `/api/v2/auth/login` | POST | `services/auth/` | User login |
| `/api/v2/auth/register` | POST | `services/auth/`, `services/email/` | User registration |
| `/api/v2/auth/logout` | POST | `services/auth/` | User logout |
| `/api/v2/auth/refresh` | POST | `services/auth/` | Token refresh |
| `/api/v2/auth/password-reset` | POST | `services/auth/`, `services/email/` | Request password reset |
| `/api/v2/auth/password-reset/confirm` | POST | `services/auth/` | Complete password reset |
| `/api/v2/users/me` | GET | `services/auth/` | Get current user |
| `/api/v2/users/me` | PATCH | `services/auth/` | Update profile |
| `/api/v2/products` | GET | `services/catalog/` | List products |
| `/api/v2/products/:id` | GET | `services/catalog/` | Get product |
| `/api/v2/products` | POST | `services/catalog/` | Create product |
| `/api/v2/products/:id` | PATCH | `services/catalog/` | Update product |
| `/api/v2/products/:id` | DELETE | `services/catalog/` | Delete product |
| `/api/v2/cart` | GET | `services/cart/` | Get cart |
| `/api/v2/cart/items` | POST | `services/cart/` | Add to cart |
| `/api/v2/cart/items/:id` | PATCH | `services/cart/` | Update cart item |
| `/api/v2/cart/items/:id` | DELETE | `services/cart/` | Remove cart item |
| `/api/v2/checkout` | POST | `services/orders/`, `services/billing/` | Start checkout |
| `/api/v2/orders` | GET | `services/orders/` | List orders |
| `/api/v2/orders/:id` | GET | `services/orders/` | Get order |
| `/api/v2/orders/:id/cancel` | POST | `services/orders/` | Cancel order |
| `/api/v2/subscriptions` | GET | `services/billing/` | List subscriptions |
| `/api/v2/subscriptions` | POST | `services/billing/` | Create subscription |
| `/api/v2/subscriptions/:id` | PATCH | `services/billing/` | Update subscription |
| `/api/v2/subscriptions/:id/cancel` | POST | `services/billing/` | Cancel subscription |
| `/api/v2/organizations` | POST | `services/org/` | Create organization |
| `/api/v2/organizations/:id` | GET | `services/org/` | Get organization |
| `/api/v2/organizations/:id` | PATCH | `services/org/` | Update organization |
| `/api/v2/organizations/:id/members` | GET | `services/org/` | List members |
| `/api/v2/organizations/:id/invitations` | POST | `services/org/` | Invite member |
| `/api/v2/reports` | POST | `services/reports/` | Generate report |
| `/api/v2/reports/:id` | GET | `services/reports/` | Get report |
| `/api/v2/reports/:id/export` | POST | `services/reports/` | Export report |
| `/api/v2/files/upload` | POST | `services/storage/` | Upload file |
| `/api/v2/files/:id` | GET | `services/storage/` | Download file |
| `/api/v2/files/:id` | DELETE | `services/storage/` | Delete file |
| `/api/v2/search` | GET | `services/search/` | Full-text search |
| `/api/v2/notifications` | GET | `services/notifications/` | List notifications |
| `/api/v2/notifications/preferences` | GET | `services/notifications/` | Get preferences |
| `/api/v2/notifications/preferences` | PATCH | `services/notifications/` | Update preferences |
| `/api/v2/webhooks` | POST | `services/webhooks/` | Create webhook |
| `/api/v2/webhooks/:id` | PATCH | `services/webhooks/` | Update webhook |
| `/api/v2/webhooks/:id` | DELETE | `services/webhooks/` | Delete webhook |
| `/api/v2/audit-logs` | GET | `services/audit/` | Query audit logs |
| `/api/v1/*` (legacy) | ALL | `legacy/` | Legacy v1 API — DO NOT MODIFY |

### 1.5 Features → Workflows

| Feature ID | Workflow | Workflow Steps |
|---|---|---|
| F-002 | Registration | Signup Form -> Validate -> Create User -> Send Verification Email -> Verify Email -> Redirect to Dashboard |
| F-004 | Password Reset | Request Reset -> Validate Email -> Generate Token -> Send Reset Email -> Click Link -> Verify Token -> Update Password -> Notify User |
| F-009 | Checkout | Review Cart -> Calculate Totals -> Validate Coupon -> Collect Payment Info -> Process Payment -> Create Order -> Update Inventory -> Send Confirmation -> Redirect to Order |
| F-008 | Cart Management | Add Item -> Update Quantity -> Calculate Subtotal -> Apply Discounts -> Check Stock -> Save Cart |
| F-011 | Subscription Lifecycle | Create Subscription -> Trial Period -> First Payment -> Active -> Renewal -> Cancel -> Grace Period -> Expired |
| F-010 | Order Fulfillment | Order Placed -> Payment Confirmed -> Pick Items -> Pack -> Generate Label -> Ship -> Track -> Delivered |
| F-012 | Report Generation | Select Report Type -> Configure Parameters -> Build Query -> Execute Query -> Format Output -> Deliver (Download/Email/Schedule) |
| F-013 | File Upload | Select File -> Validate Type -> Scan for Malware -> Upload to Storage -> Create DB Record -> Generate Thumbnail -> Return URL |
| F-005 | Org Onboarding | Create Org -> Configure Domain -> Setup SSO -> Invite Members -> Assign Roles -> Configure Billing |
| F-015 | Notification Dispatch | Trigger Event -> Determine Channels -> Check Preferences -> Render Template -> Queue Delivery -> Send -> Log Delivery |

### 1.6 Features → API Endpoints

| Feature ID | Feature Name | API Endpoints Used |
|---|---|---|
| F-001 | User Authentication | POST `/api/v2/auth/login`, POST `/api/v2/auth/logout`, POST `/api/v2/auth/refresh` |
| F-002 | User Registration | POST `/api/v2/auth/register`, POST `/api/v2/auth/verify-email` |
| F-003 | User Profile | GET `/api/v2/users/me`, PATCH `/api/v2/users/me` |
| F-004 | Password Reset | POST `/api/v2/auth/password-reset`, POST `/api/v2/auth/password-reset/confirm` |
| F-005 | Org Management | POST/GET/PATCH `/api/v2/organizations/:id/*` |
| F-006 | RBAC | Middleware on most endpoints, admin endpoints for role management |
| F-007 | Product Catalog | GET/POST/PATCH/DELETE `/api/v2/products/*` |
| F-008 | Shopping Cart | GET `/api/v2/cart`, POST/PATCH/DELETE `/api/v2/cart/items/*` |
| F-009 | Checkout | POST `/api/v2/checkout`, integration with payment gateway |
| F-010 | Order Management | GET `/api/v2/orders/*`, POST `/api/v2/orders/:id/cancel` |
| F-011 | Subscriptions | GET/POST/PATCH `/api/v2/subscriptions/*` |
| F-012 | Reports | POST/GET `/api/v2/reports/*`, POST `/api/v2/reports/:id/export` |
| F-013 | File Upload | POST `/api/v2/files/upload`, GET/DELETE `/api/v2/files/:id` |
| F-014 | Search | GET `/api/v2/search?q=*` |
| F-015 | Notifications | GET `/api/v2/notifications`, PATCH `/api/v2/notifications/preferences` |
| F-016 | Audit Logging | POST (internal) audit events, GET `/api/v2/audit-logs` |
| F-017 | API Keys | POST/GET/DELETE `/api/v2/api-keys` |
| F-018 | Webhooks | POST/PATCH/DELETE `/api/v2/webhooks/*` |
| F-019 | Data Export | POST `/api/v2/reports/:id/export` |

### 1.7 Features → Database Tables

| Feature ID | Feature Name | Primary Tables | Secondary Tables |
|---|---|---|---|
| F-001 | Auth | `users`, `sessions` | `roles`, `permissions` |
| F-002 | Registration | `users` | `email_queue`, `email_logs` |
| F-003 | Profile | `users` | — |
| F-005 | Organizations | `organizations` | `teams`, `team_members`, `invitations` |
| F-006 | RBAC | `roles`, `permissions` | `users` |
| F-007 | Catalog | `products`, `categories` | `product_variants`, `inventory` |
| F-008 | Cart | `carts`, `cart_items` | `products` |
| F-009 | Checkout | `orders`, `order_items` | `payments`, `subscriptions` |
| F-010 | Orders | `orders`, `order_items` | `shipments`, `cancellations` |
| F-011 | Subscriptions | `subscriptions`, `plans` | `payments`, `invoices` |
| F-012 | Reports | `reports`, `report_schedules` | `export_logs` |
| F-013 | Files | `files` | `file_versions`, `storage_quotas` |
| F-014 | Search | `search_index` | `products`, `search_synonyms` |
| F-015 | Notifications | `notifications`, `notification_preferences` | `notification_logs` |
| F-016 | Audit | `audit_events` | `audit_event_details` |
| F-018 | Webhooks | `webhook_configs` | `webhook_deliveries` |

### 1.8 Features → Tests

| Feature ID | Feature Name | Test Files | Test Type |
|---|---|---|---|
| F-001 | Auth | `services/auth/tests/authService.test.ts` | Unit |
| F-001 | Auth | `services/auth/tests/authController.test.ts` | Integration |
| F-001 | Auth | `services/auth/tests/session.test.ts` | Unit |
| F-002 | Registration | `services/auth/tests/registration.test.ts` | Integration |
| F-002 | Registration | `apps/web/tests/registration.test.ts` | E2E |
| F-004 | Password Reset | `services/auth/tests/passwordReset.test.ts` | Integration |
| F-007 | Catalog | `services/catalog/tests/productService.test.ts` | Unit |
| F-007 | Catalog | `services/catalog/tests/productRepository.test.ts` | Unit |
| F-008 | Cart | `services/cart/tests/cartService.test.ts` | Unit |
| F-009 | Checkout | `services/orders/tests/checkout.test.ts` | Integration |
| F-009 | Checkout | `apps/web/tests/checkout.e2e.ts` | E2E |
| F-010 | Orders | `services/orders/tests/orderService.test.ts` | Unit |
| F-010 | Orders | `services/orders/tests/cancellation.test.ts` | Unit |
| F-011 | Subscriptions | `services/billing/tests/subscription.test.ts` | Integration |
| F-011 | Subscriptions | `services/billing/tests/billingRules.test.ts` | Unit |
| F-012 | Reports | `services/reports/tests/reportService.test.ts` | Unit |
| F-013 | Files | `services/storage/tests/fileService.test.ts` | Unit |
| F-013 | Files | `services/storage/tests/upload.test.ts` | Integration |
| F-015 | Notifications | `services/notifications/tests/notificationService.test.ts` | Unit |
| F-016 | Audit | `services/audit/tests/auditService.test.ts` | Unit |
| F-018 | Webhooks | `services/webhooks/tests/webhookService.test.ts` | Unit |
| F-018 | Webhooks | `services/webhooks/tests/delivery.test.ts` | Integration |

---

## 2. Dependency Chain Map

### 2.1 User Registration Chain

```
User Registration (F-002)
├── Frontend: apps/web/src/pages/register.tsx
│   └── API Client: apps/web/src/api/auth.ts
│       └── POST /api/v2/auth/register
│           ├── Middleware: rateLimiter.ts
│           ├── Middleware: requestLogger.ts
│           ├── Controller: services/auth/src/authController.ts#register
│           │   ├── Validation: services/auth/src/validation.ts (zod schema)
│           │   └── Service: services/auth/src/authService.ts#register
│           │       ├── UserRepository: services/auth/src/userRepository.ts
│           │       │   └── Database: users table
│           │       ├── EmailService: services/email/src/emailService.ts
│           │       │   ├── EmailQueue: services/email/src/emailQueue.ts (bull/Redis)
│           │       │   └── Provider: services/email/src/providers/sendgrid.ts
│           │       │       └── External: SendGrid API
│           │       ├── AuditService: services/audit/src/auditService.ts
│           │       │   └── Database: audit_events table
│           │       └── SessionService: services/auth/src/session.ts
│           │           └── Database: sessions table
│           └── Response: { user, token, expiresIn }
│               └── Frontend stores token, redirects to dashboard
```

### 2.2 Checkout & Payment Chain

```
Checkout (F-009)
├── Frontend: apps/web/src/pages/checkout.tsx
│   └── API Client: apps/web/src/api/checkout.ts
│       └── POST /api/v2/checkout
│           ├── Middleware: requireAuth.ts
│           ├── Middleware: rateLimiter.ts
│           ├── Middleware: rbac.ts (checkout permission)
│           ├── Controller: services/orders/src/orderController.ts#checkout
│           │   ├── Validation: zod checkout schema
│           │   └── Service: services/orders/src/orderService.ts#checkout
│           │       ├── CartService: services/cart/src/cartService.ts
│           │       │   └── Database: carts, cart_items tables
│           │       ├── ProductService: services/catalog/src/productService.ts
│           │       │   └── Database: products, inventory tables
│           │       ├── BillingService: services/billing/src/paymentService.ts
│           │       │   ├── Rules: services/billing/src/rules/discounts.ts
│           │       │   ├── Rules: services/billing/src/rules/trial.ts
│           │       │   └── Gateway: services/billing/src/gateways/stripe.ts
│           │       │       └── External: Stripe API
│           │       ├── OrderRepository: services/orders/src/orderRepository.ts
│           │       │   └── Database: orders, order_items tables
│           │       ├── AuditService: services/audit/src/auditService.ts
│           │       │   └── Database: audit_events table
│           │       └── NotificationService: services/notifications/src/notificationService.ts
│           │           ├── Email Channel: services/notifications/src/channels/email.ts
│           │           │   └── EmailService -> SendGrid
│           │           └── Database: notifications table
```

### 2.3 Report Generation Chain

```
Report Generation (F-012)
├── Frontend: apps/web/src/pages/reports/[id].tsx
│   └── API Client: apps/web/src/api/reports.ts
│       └── POST /api/v2/reports
│           ├── Middleware: requireAuth.ts
│           ├── Middleware: rbac.ts (report:generate)
│           ├── Controller: services/reports/src/reportController.ts
│           │   └── Service: services/reports/src/reportService.ts
│           │       ├── QueryBuilder: services/reports/src/queryBuilder.ts
│           │       │   └── Database: dynamic query (multiple tables)
│           │       ├── ExportService: services/reports/src/export.ts
│           │       │   └── File generation (CSV/PDF/XLSX)
│           │       ├── StorageService: services/storage/src/fileService.ts
│           │       │   └── S3 Provider: services/storage/src/providers/s3.ts
│           │       ├── Scheduler: services/reports/src/scheduler.ts
│           │       │   └── Bull queue (cron jobs via Redis)
│           │       └── NotificationService: sends report ready notification
│           └── Response: { reportId, status, downloadUrl }
```

### 2.4 Subscription Lifecycle Chain

```
Subscription Lifecycle (F-011)
├── Create Subscription
│   └── POST /api/v2/subscriptions
│       ├── Service: services/billing/src/subscriptionService.ts
│       │   ├── Database: subscriptions table
│       │   ├── Rules: services/billing/src/rules/trial.ts
│       │   ├── PaymentService: services/billing/src/paymentService.ts
│       │   │   └── Stripe Gateway
│       │   ├── InvoiceService: services/billing/src/invoiceService.ts
│       │   │   └── Database: invoices table
│       │   └── NotificationService
│       └── Response: { subscription, invoice, trialEnd }
│
├── Renewal (via cron / webhook)
│   ├── Bull Job: subscription-renewal queue
│   │   ├── PaymentService -> charge -> success/failure
│   │   ├── On success: extend subscription, send receipt
│   │   └── On failure: start grace period, notify user
│   └── Database: subscriptions.status updated
│
└── Cancellation
    └── POST /api/v2/subscriptions/:id/cancel
        ├── Service: subscriptionService.cancel()
        ├── Rules: refund eligibility check
        ├── Database: subscriptions.status = 'cancelled'
        ├── InvoiceService: generate final invoice
        └── NotificationService: send cancellation confirmation
```

---

## 3. Impact Chain Map

### 3.1 If `services/auth/` Changes

```
If AuthService changes:
  Affects files:
    apps/web/src/api/auth.ts
    apps/web/src/hooks/useAuth.ts
    apps/web/src/pages/login.tsx
    apps/web/src/pages/register.tsx
    apps/web/src/pages/reset-password.tsx
    apps/web/src/components/ProtectedRoute.tsx
    middleware/requireAuth.ts
    middleware/rbac.ts
    services/email/src/emailService.ts (sends verification emails)
    services/audit/src/auditService.ts (logs auth events)
    services/org/src/invitationService.ts (uses auth for invite flow)
    services/webhooks/src/webhookService.ts (auth for webhook verification)
  Affects workflows:
    Registration, Login, Password Reset, Session Management
    Multi-tenant SSO, API Key Auth
  Affects features:
    F-001 (Auth), F-002 (Registration), F-003 (Profile), F-004 (Password Reset)
    F-005 (Org), F-006 (RBAC), F-017 (API Keys)
  Risk: HIGH
  Downtime impact: CRITICAL — all services depend on auth
```

### 3.2 If `services/billing/` Changes

```
If BillingService changes:
  Affects files:
    services/orders/src/orderService.ts
    apps/web/src/pages/checkout.tsx
    apps/web/src/pages/billing.tsx
    apps/web/src/pages/subscription.tsx
    services/email/src/emailService.ts (receipts, invoices)
    services/notifications/src/notificationService.ts (billing alerts)
  Affects workflows:
    Checkout, Subscription Lifecycle, Renewal, Refund
    Invoice Generation, Payment Processing
  Affects features:
    F-009 (Checkout), F-011 (Subscriptions)
  Risk: HIGH
  Financial impact: CRITICAL — payment processing
  Regulatory impact: PCI compliance, audit trail requirements
```

### 3.3 If `services/catalog/` Changes

```
If CatalogService changes:
  Affects files:
    apps/web/src/pages/products/
    apps/web/src/pages/categories/
    services/cart/src/cartService.ts
    services/orders/src/orderService.ts
    services/search/src/indexService.ts
    services/search/src/searchService.ts
  Affects workflows:
    Product browsing, Cart Management, Checkout (inventory check)
    Search indexing
  Affects features:
    F-007 (Catalog), F-008 (Cart), F-009 (Checkout)
    F-014 (Search)
  Risk: MEDIUM
  User impact: Product unavailability, incorrect inventory
```

### 3.4 If `services/orders/` Changes

```
If OrdersService changes:
  Affects files:
    apps/web/src/pages/checkout.tsx
    apps/web/src/pages/orders/
    services/billing/src/paymentService.ts
    services/notifications/src/notificationService.ts
    services/audit/src/auditService.ts
  Affects workflows:
    Checkout, Order Fulfillment, Cancellation, Shipping
  Affects features:
    F-009 (Checkout), F-010 (Order Management)
  Risk: HIGH
  Business impact: Revenue-critical, order processing
```

### 3.5 If `services/storage/` Changes

```
If StorageService changes:
  Affects files:
    apps/web/src/pages/files/
    apps/web/src/components/FileUploader.tsx
    services/reports/src/export.ts
  Affects workflows:
    File Upload, Report Export, Thumbnail Generation
  Affects features:
    F-013 (File Upload), F-019 (Data Export), F-012 (Reports)
  Risk: MEDIUM
  Data impact: File availability, quota enforcement
```

### 3.6 If `services/notifications/` Changes

```
If NotificationService changes:
  Affects files:
    services/auth/src/authService.ts
    services/orders/src/orderService.ts
    services/billing/src/subscriptionService.ts
    apps/web/src/pages/notifications/
  Affects workflows:
    All workflows with async notifications
  Affects features:
    F-015 (Notifications), F-002 (Registration email), F-004 (Password Reset)
    F-009 (Checkout confirmation), F-011 (Subscription alerts)
  Risk: MEDIUM
  User impact: Missing critical communications
```

### 3.7 If `services/audit/` Changes

```
If AuditService changes:
  Affects files:
    services/auth/src/authService.ts (audit logs)
    services/billing/src/paymentService.ts (audit logs)
    services/orders/src/orderService.ts (audit logs)
    services/org/src/orgService.ts (audit logs)
  Affects workflows:
    All workflows with audit requirements
  Affects features:
    F-016 (Audit Logging)
    Compliance: SOC2, PCI DSS, GDPR
  Risk: MEDIUM
  Compliance impact: ALL financial and auth operations must be audited
```

### 3.8 If `services/search/` Changes

```
If SearchService changes:
  Affects files:
    apps/web/src/pages/search/
    services/catalog/src/productService.ts
  Affects workflows:
    Product Search, Index Build, Synonym Management
  Affects features:
    F-014 (Search)
  Risk: LOW
  User impact: Search functionality degraded or unavailable
```

### 3.9 If `apps/web/` Changes

```
If Frontend changes:
  Affects files:
    All services indirectly (contract through API)
  Affects features:
    ALL user-facing features (F-001 through F-019)
  Risk: HIGH
  User impact: FULL — user interface
  Note: API changes must be coordinated; frontend may depend on specific response shapes
```

### 3.10 If `middleware/` Changes

```
If Middleware changes:
  Affects files:
    ALL route handlers across all services
    apps/web/src/api/* (if API contract changes)
  Affects features:
    F-001 (Auth — requireAuth), F-006 (RBAC)
    ALL features (rate limiting), ALL features (error handling)
  Risk: HIGH
  User impact: System-wide authentication, rate limiting, or error handling changes
```

---

## 4. Ownership Map

### 4.1 Files → Team/Person

| File/Module | Primary Owner | Secondary | Contact |
|---|---|---|---|
| `services/auth/` | Auth Team | Platform Team | #team-auth |
| `services/billing/` | Billing Team | Payments Team | #team-billing |
| `services/orders/` | Orders Team | Fulfillment Team | #team-orders |
| `services/catalog/` | Catalog Team | Merchandising | #team-catalog |
| `services/cart/` | Cart Team | Checkout Team | #team-cart |
| `services/org/` | Platform Team | Auth Team | #team-platform |
| `services/reports/` | Analytics Team | Data Team | #team-analytics |
| `services/storage/` | Infrastructure Team | Platform Team | #team-infra |
| `services/notifications/` | Communication Team | Platform Team | #team-comm |
| `services/audit/` | Security Team | Compliance Team | #team-security |
| `services/search/` | Search Team | Catalog Team | #team-search |
| `services/webhooks/` | Integrations Team | Platform Team | #team-integrations |
| `services/email/` | Communication Team | Auth Team | #team-comm |
| `apps/web/` | Frontend Team | Design Team | #team-frontend |
| `middleware/` | Platform Team | Security Team | #team-platform |
| `infra/` | DevOps Team | Infrastructure Team | #team-devops |
| `legacy/` | Platform Team (maintenance only) | — | #team-platform |
| `packages/shared/` | Platform Team | All Teams | #team-platform |
| `packages/db/` | Data Team | Platform Team | #team-data |

### 4.2 Modules → Primary Maintainer

| Module | Maintainer | Backup | Review Required |
|---|---|---|---|
| Auth Service | Alice Chen | Bob Kumar | Security review |
| Billing Service | Bob Kumar | Carol Davis | Financial review |
| Orders Service | Carol Davis | David Lee | Product review |
| Catalog Service | David Lee | Alice Chen | Product review |
| Cart Service | Eve Martin | Frank Zhang | Product review |
| Org Service | Frank Zhang | Grace Kim | Architecture review |
| Reports Service | Grace Kim | Henry Wu | Data review |
| Storage Service | Henry Wu | Irene Sato | Security review |
| Notifications Service | Irene Sato | Jack Brown | Architecture review |
| Audit Service | Jack Brown | Alice Chen | Security review |
| Search Service | Kate Liu | David Lee | Performance review |
| Webhooks Service | Liam Patel | Irene Sato | Architecture review |
| Frontend App | Maria Garcia | Eve Martin | UX review |
| Infrastructure | Noah Wilson | Henry Wu | DevOps review |

### 4.3 Workflows → Process Owner

| Workflow | Process Owner | Business Stakeholder |
|---|---|---|
| Registration | Alice Chen | Product Manager |
| Checkout | Bob Kumar | Product Manager |
| Order Fulfillment | Carol Davis | Operations Manager |
| Subscription Lifecycle | Bob Kumar | Finance Manager |
| Report Generation | Grace Kim | Analytics Manager |
| File Upload | Henry Wu | Product Manager |
| Password Reset | Alice Chen | Security Manager |
| Notification Dispatch | Irene Sato | Marketing Manager |
| Multi-tenant Onboarding | Frank Zhang | Sales Manager |
| Webhook Delivery | Liam Patel | Integrations Manager |

### 4.4 API Endpoints → API Owner

| Endpoint Group | API Owner | Team |
|---|---|---|
| `/api/v2/auth/*` | Alice Chen | Auth Team |
| `/api/v2/users/*` | Alice Chen | Auth Team |
| `/api/v2/products/*` | David Lee | Catalog Team |
| `/api/v2/cart/*` | Eve Martin | Cart Team |
| `/api/v2/checkout` | Bob Kumar | Billing Team |
| `/api/v2/orders/*` | Carol Davis | Orders Team |
| `/api/v2/subscriptions/*` | Bob Kumar | Billing Team |
| `/api/v2/organizations/*` | Frank Zhang | Platform Team |
| `/api/v2/reports/*` | Grace Kim | Analytics Team |
| `/api/v2/files/*` | Henry Wu | Infrastructure Team |
| `/api/v2/search` | Kate Liu | Search Team |
| `/api/v2/notifications/*` | Irene Sato | Communication Team |
| `/api/v2/webhooks/*` | Liam Patel | Integrations Team |
| `/api/v2/audit-logs` | Jack Brown | Security Team |
| `/api/v2/api-keys` | Alice Chen | Auth Team |
| `/api/v1/*` (legacy) | Frank Zhang | Platform Team |

### 4.5 Database Tables → Data Owner

| Table | Data Owner | Team | Sensitivity |
|---|---|---|---|
| `users` | Alice Chen | Auth | PII — HIGH |
| `sessions` | Alice Chen | Auth | HIGH |
| `roles` | Frank Zhang | Platform | MEDIUM |
| `permissions` | Frank Zhang | Platform | MEDIUM |
| `api_keys` | Alice Chen | Auth | HIGH |
| `organizations` | Frank Zhang | Platform | MEDIUM |
| `teams` | Frank Zhang | Platform | LOW |
| `team_members` | Frank Zhang | Platform | MEDIUM |
| `invitations` | Frank Zhang | Platform | LOW |
| `products` | David Lee | Catalog | LOW |
| `categories` | David Lee | Catalog | LOW |
| `product_variants` | David Lee | Catalog | LOW |
| `inventory` | David Lee | Catalog | MEDIUM |
| `carts` | Eve Martin | Cart | MEDIUM |
| `cart_items` | Eve Martin | Cart | LOW |
| `orders` | Carol Davis | Orders | MEDIUM |
| `order_items` | Carol Davis | Orders | MEDIUM |
| `shipments` | Carol Davis | Orders | LOW |
| `cancellations` | Carol Davis | Orders | MEDIUM |
| `payments` | Bob Kumar | Billing | FINANCIAL — HIGH |
| `invoices` | Bob Kumar | Billing | FINANCIAL — HIGH |
| `subscriptions` | Bob Kumar | Billing | MEDIUM |
| `plans` | Bob Kumar | Billing | LOW |
| `discounts` | Bob Kumar | Billing | LOW |
| `reports` | Grace Kim | Analytics | MEDIUM |
| `report_schedules` | Grace Kim | Analytics | LOW |
| `export_logs` | Grace Kim | Analytics | LOW |
| `files` | Henry Wu | Infrastructure | MEDIUM |
| `file_versions` | Henry Wu | Infrastructure | LOW |
| `storage_quotas` | Henry Wu | Infrastructure | LOW |
| `notifications` | Irene Sato | Communication | LOW |
| `notification_preferences` | Irene Sato | Communication | LOW |
| `notification_logs` | Irene Sato | Communication | LOW |
| `audit_events` | Jack Brown | Security | HIGH |
| `audit_event_details` | Jack Brown | Security | HIGH |
| `search_index` | Kate Liu | Search | LOW |
| `search_synonyms` | Kate Liu | Search | LOW |
| `webhook_configs` | Liam Patel | Integrations | MEDIUM |
| `webhook_deliveries` | Liam Patel | Integrations | LOW |
| `email_queue` | Irene Sato | Communication | LOW |
| `email_logs` | Irene Sato | Communication | MEDIUM |
| `email_templates` | Irene Sato | Communication | LOW |

---

## 5. Communication Flow Map

### 5.1 Primary Request Flow

```
┌─────────┐     ┌──────────┐     ┌─────────────┐     ┌─────────────────┐
│  User    │────▶│  Browser  │────▶│  React App   │────▶│  API Client     │
│          │     │  (Client) │     │  (SPA/SSR)   │     │  (axios/fetch)  │
└─────────┘     └──────────┘     └─────────────┘     └─────────────────┘
                                                               │
                                                               ▼
                                                ┌─────────────────────────┐
                                                │     API Gateway         │
                                                │  (Rate Limiting, Auth   │
                                                │   Validation, Routing)  │
                                                └─────────────────────────┘
                                                               │
                                                               ▼
                                                ┌─────────────────────────┐
                                                │   Auth Middleware        │
                                                │  (JWT Verification,     │
                                                │   RBAC Check)          │
                                                └─────────────────────────┘
                                                               │
                                                               ▼
                                                ┌─────────────────────────┐
                                                │    Route Handler         │
                                                │  (Request Parsing,      │
                                                │   Response Formatting)  │
                                                └─────────────────────────┘
                                                               │
                                                               ▼
                                                ┌─────────────────────────┐
                                                │     Controller           │
                                                │  (Orchestration,        │
                                                │   Validation)           │
                                                └─────────────────────────┘
                                                               │
                                                               ▼
                                                ┌─────────────────────────┐
                                                │     Service Layer        │
                                                │  (Business Logic,       │
                                                │   Rules Engine)         │
                                                └─────────────────────────┘
                                                      │           │
                                                      ▼           ▼
                                          ┌─────────────┐  ┌──────────────┐
                                          │  Repository  │  │ External API │
                                          │  (Data       │  │ (Stripe,     │
                                          │   Access)    │  │  SendGrid)   │
                                          └─────────────┘  └──────────────┘
                                                │                  │
                                                ▼                  ▼
                                          ┌─────────────┐
                                          │  Database    │
                                          │ (PostgreSQL, │
                                          │  Redis)      │
                                          └─────────────┘
```

### 5.2 Event-Driven Flow (Async)

```
┌──────────┐     ┌──────────────┐     ┌────────────┐     ┌───────────────┐
│ Service A │────▶│ Event Emitter │────▶│  Message    │────▶│  Queue/Event  │
│ (Producer)│     │              │     │  Broker     │     │   Bus         │
└──────────┘     └──────────────┘     │ (Redis Pub/ │     │  (Bull/Redis) │
                                      │  Sub/Rabbit)│     └───────────────┘
                                      └────────────┘              │
                                                                  ▼
                                                        ┌───────────────────┐
                                                        │  Worker / Consumer │
                                                        │  (Background Job)  │
                                                        └───────────────────┘
                                                               │
                                                               ▼
                                                        ┌───────────────────┐
                                                        │   Service B       │
                                                        │  (Consumer)       │
                                                        └───────────────────┘
```

### 5.3 Notification Flow

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Any Service  │────▶│ Notification     │────▶│ Preferences       │
│ (Trigger     │     │ Service          │     │ Check             │
│  Event)      │     │                  │     │ (User Opt-in/out) │
└─────────────┘     └──────────────────┘     └───────────────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────────┐
                                              │  Channel Router     │
                                              └─────────────────────┘
                                          ┌─────────┬─────────┬──────────┐
                                          ▼         ▼         ▼
                                   ┌──────────┐ ┌────────┐ ┌──────────┐
                                   │ Email     │ │ Slack  │ │ Push     │
                                   │ Channel   │ │ Channel│ │ Channel  │
                                   └──────────┘ └────────┘ └──────────┘
                                          │
                                          ▼
                                   ┌──────────────┐     ┌────────────┐
                                   │ Email Service │────▶│ SendGrid   │
                                   │ (Queue)       │     │ /SES       │
                                   └──────────────┘     └────────────┘
```

### 5.4 Webhook Delivery Flow

```
┌──────────────┐     ┌─────────────────┐     ┌────────────────────┐
│ Internal      │────▶│ Webhook Service  │────▶│ Delivery Scheduler │
│ Event         │     │ (Event -> Payload│     │ (Retry Logic,      │
│ (Order.placed)│     │  -> Match        │     │  Backoff,          │
└──────────────┘     │  Subscribers)    │     │  Rate Limiting)    │
                     └─────────────────┘     └────────────────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────────┐
                                              │ HTTP POST to        │
                                              │ Subscriber URL      │
                                              └─────────────────────┘
                                                         │
                                              ┌──────────┴──────────┐
                                              ▼                     ▼
                                     ┌──────────────┐    ┌──────────────────┐
                                     │ Success (2xx) │    │ Failure (4xx/5xx)│
                                     │ Log Success   │    │ Retry Queue      │
                                     └──────────────┘    │ (max 5 attempts) │
                                                          └──────────────────┘
                                                                     │
                                                            ┌────────┴────────┐
                                                            ▼                 ▼
                                                    ┌────────────┐  ┌─────────────────┐
                                                    │ All Retry  │  │ Mark as Failed  │
                                                    │ Exhausted  │  │ Notify Owner    │
                                                    └────────────┘  └─────────────────┘
```

### 5.5 Database Migration Flow

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────────┐
│ Developer     │────▶│ Migration File  │────▶│ Migration Runner     │
│ Creates      │     │ (YYYYMMDD_desc  │     │ (sequelize-cli /     │
│ migration    │     │  .ts)           │     │  custom script)      │
└──────────────┘     └─────────────────┘     └──────────────────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────────┐
                                              │ Pre-Deploy Check    │
                                              │ (Dry Run migration  │
                                              │  against staging)   │
                                              └─────────────────────┘
                                                         │
                                              ┌──────────┴──────────┐
                                              ▼                     ▼
                                     ┌────────────────┐  ┌──────────────────┐
                                     │ Deploy to Prod │  │ Rollback Script  │
                                     │ (Migration up) │  │ (Migration down) │
                                     └────────────────┘  └──────────────────┘
```

---

## 6. Cross-Reference Index

### A

| Entity | Appears In | Type |
|---|---|---|
| `api_keys` table | Section 1.3, 4.5 | Database Table |
| API Gateway | Section 5.1, 5.5 | Component |
| `api/v1/*` (legacy) | Section 1.4, 4.4 | API Endpoint |
| `api/v2/audit-logs` | Section 1.4, 4.4 | API Endpoint |
| `api/v2/auth/*` | Section 1.4, 4.4 | API Endpoint |
| `api/v2/cart/*` | Section 1.4, 4.4 | API Endpoint |
| `api/v2/checkout` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/files/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/notifications/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/orders/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/organizations/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/products/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/reports/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/search` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/subscriptions/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/users/*` | Section 1.4, 4.4 | API Endpoint |
| `/api/v2/webhooks/*` | Section 1.4, 4.4 | API Endpoint |
| Audit Logging (F-016) | Section 1.1, 1.6, 1.7, 1.8, 3.7 | Feature |
| Audit Service | Section 1.3, 1.4, 3.7, 4.1, 4.2 | Service |
| Auth Service | Section 1.3, 1.4, 3.1, 4.1, 4.2 | Service |
| Auth Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |

### B

| Entity | Appears In | Type |
|---|---|---|
| Billing Service | Section 1.3, 3.2, 4.1, 4.2 | Service |
| Billing Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |

### C

| Entity | Appears In | Type |
|---|---|---|
| Cart Management (F-008) | Section 1.1, 1.5, 1.6, 1.7, 1.8 | Feature |
| Cart Service | Section 1.3, 4.1, 4.2 | Service |
| Cart Team | Section 4.1, 4.2, 4.4, 4.5 | Team |
| Catalog Service | Section 1.3, 3.3, 4.1, 4.2 | Service |
| Catalog Team | Section 4.1, 4.2, 4.3, 4.5 | Team |
| Checkout (F-009) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.2 | Feature |
| CI/CD Pipeline | Section 1.4 (model-replacement-test) | Workflow |
| Communication Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |

### D

| Entity | Appears In | Type |
|---|---|---|
| Data Export (F-019) | Section 1.1, 1.6, 3.5 | Feature |
| Data Team | Section 4.1, 4.2 | Team |
| DevOps Team | Section 4.1, 4.2 | Team |

### E

| Entity | Appears In | Type |
|---|---|---|
| Email Service | Section 1.3, 4.1 | Service |
| Event-Driven Flow | Section 5.2 | Communication Flow |

### F

| Entity | Appears In | Type |
|---|---|---|
| F-001 (Auth) | Section 1.1, 1.6, 1.7, 1.8, 3.1 | Feature |
| F-002 (Registration) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.1 | Feature |
| F-003 (Profile) | Section 1.1, 1.6, 1.7, 3.1 | Feature |
| F-004 (Password Reset) | Section 1.1, 1.5, 1.6, 1.7, 3.1 | Feature |
| F-005 (Organizations) | Section 1.1, 1.5, 1.6, 1.7, 3.1 | Feature |
| F-006 (RBAC) | Section 1.1, 1.6, 3.1 | Feature |
| F-007 (Catalog) | Section 1.1, 1.6, 1.7, 1.8, 3.3 | Feature |
| F-008 (Cart) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 3.3 | Feature |
| F-009 (Checkout) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.2, 3.2 | Feature |
| F-010 (Orders) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 3.4 | Feature |
| F-011 (Subscriptions) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.4, 3.2 | Feature |
| F-012 (Reports) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.3, 3.5 | Feature |
| F-013 (File Upload) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 3.5 | Feature |
| F-014 (Search) | Section 1.1, 1.6, 1.7, 3.3, 3.8 | Feature |
| F-015 (Notifications) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 3.6 | Feature |
| F-016 (Audit) | Section 1.1, 1.6, 1.7, 1.8, 3.7 | Feature |
| F-017 (API Keys) | Section 1.1, 1.6, 3.1 | Feature |
| F-018 (Webhooks) | Section 1.1, 1.6, 1.7, 1.8 | Feature |
| F-019 (Data Export) | Section 1.1, 1.6 | Feature |
| F-020 (Team Collaboration) | Section 1.1 | Feature (Planned) |
| F-101 (Legacy v1) | Section 1.1 | Feature (Deprecated) |
| File Upload (F-013) | Section 1.1, 1.5, 1.6, 1.7, 1.8 | Feature |
| Frontend App (`apps/web/`) | Section 1.2, 3.9, 4.1 | Module |

### G

| Entity | Appears In | Type |
|---|---|---|
| GraphQL Gateway | Section 1.1 (model-replacement-test) | Architecture |

### I

| Entity | Appears In | Type |
|---|---|---|
| Infrastructure Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |
| Integrations Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |

### L

| Entity | Appears In | Type |
|---|---|---|
| Legacy v1 (`legacy/`) | Section 1.1, 4.1 | Module |
| Legacy v1 API (F-101) | Section 1.1 | Feature (Deprecated) |

### M

| Entity | Appears In | Type |
|---|---|---|
| Middleware | Section 1.2, 3.10, 4.1, 5.1 | Module |
| Migration Flow | Section 5.5 | Communication Flow |
| Multi-tenant Org (F-005) | Section 1.1, 1.5, 1.6, 1.7 | Feature |

### N

| Entity | Appears In | Type |
|---|---|---|
| Notification Flow | Section 5.3 | Communication Flow |
| Notification Service | Section 1.3, 3.6, 4.1, 4.2 | Service |

### O

| Entity | Appears In | Type |
|---|---|---|
| Order Fulfillment (F-010) | Section 1.1, 1.5, 1.6, 1.7, 1.8 | Feature |
| Orders Service | Section 1.3, 3.4, 4.1, 4.2 | Service |
| Orders Team | Section 4.1, 4.2, 4.3, 4.5 | Team |
| Org Service | Section 1.3, 4.1, 4.2 | Service |

### P

| Entity | Appears In | Type |
|---|---|---|
| Password Reset (F-004) | Section 1.1, 1.5, 1.6, 1.7 | Feature |
| Platform Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |
| Product Catalog (F-007) | Section 1.1, 1.6, 1.7, 1.8 | Feature |
| Profile (F-003) | Section 1.1, 1.6, 1.7 | Feature |

### R

| Entity | Appears In | Type |
|---|---|---|
| RBAC (F-006) | Section 1.1, 1.6 | Feature |
| Report Generation (F-012) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.3 | Feature |
| Reports Service | Section 1.3, 4.1, 4.2 | Service |
| Reports Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |
| Request Flow | Section 5.1 | Communication Flow |

### S

| Entity | Appears In | Type |
|---|---|---|
| Search (F-014) | Section 1.1, 1.6, 1.7 | Feature |
| Search Service | Section 1.3, 3.8, 4.1, 4.2 | Service |
| Search Team | Section 4.1, 4.2, 4.4, 4.5 | Team |
| Security Team | Section 4.1, 4.2, 4.3, 4.4, 4.5 | Team |
| Storage Service | Section 1.3, 3.5, 4.1, 4.2 | Service |
| Subscriptions (F-011) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.4 | Feature |

### T

| Entity | Appears In | Type |
|---|---|---|
| Team Collaboration (F-020) | Section 1.1 | Feature (Planned) |

### U

| Entity | Appears In | Type |
|---|---|---|
| User Authentication (F-001) | Section 1.1, 1.6, 1.7, 1.8 | Feature |
| User Registration (F-002) | Section 1.1, 1.5, 1.6, 1.7, 1.8, 2.1 | Feature |

### W

| Entity | Appears In | Type |
|---|---|---|
| Webhook Delivery Flow | Section 5.4 | Communication Flow |
| Webhook System (F-018) | Section 1.1, 1.6, 1.7, 1.8 | Feature |
| Webhooks Service | Section 1.3, 4.1, 4.2 | Service |

---

## Appendix: Index of All Entities

| # | Entity | Category | Section(s) |
|---|---|---|---|
| 1 | API Gateway | Component | 5.1, 5.5 |
| 2 | Audit Service | Service | 1.3, 1.4, 3.7, 4.1, 4.2 |
| 3 | Auth Service | Service | 1.3, 1.4, 3.1, 4.1, 4.2 |
| 4 | Billing Service | Service | 1.3, 3.2, 4.1, 4.2 |
| 5 | Cart Service | Service | 1.3, 4.1, 4.2 |
| 6 | Catalog Service | Service | 1.3, 3.3, 4.1, 4.2 |
| 7 | Email Service | Service | 1.3, 4.1 |
| 8 | F-001 — Auth | Feature | 1.1, 1.6, 1.7, 1.8, 3.1 |
| 9 | F-002 — Registration | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 2.1 |
| 10 | F-003 — Profile | Feature | 1.1, 1.6, 1.7, 3.1 |
| 11 | F-004 — Password Reset | Feature | 1.1, 1.5, 1.6, 1.7, 3.1 |
| 12 | F-005 — Organizations | Feature | 1.1, 1.5, 1.6, 1.7, 3.1 |
| 13 | F-006 — RBAC | Feature | 1.1, 1.6, 3.1 |
| 14 | F-007 — Catalog | Feature | 1.1, 1.6, 1.7, 1.8, 3.3 |
| 15 | F-008 — Cart | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 3.3 |
| 16 | F-009 — Checkout | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 2.2, 3.2 |
| 17 | F-010 — Orders | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 3.4 |
| 18 | F-011 — Subscriptions | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 2.4, 3.2 |
| 19 | F-012 — Reports | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 2.3, 3.5 |
| 20 | F-013 — File Upload | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 3.5 |
| 21 | F-014 — Search | Feature | 1.1, 1.6, 1.7, 3.3, 3.8 |
| 22 | F-015 — Notifications | Feature | 1.1, 1.5, 1.6, 1.7, 1.8, 3.6 |
| 23 | F-016 — Audit | Feature | 1.1, 1.6, 1.7, 1.8, 3.7 |
| 24 | F-017 — API Keys | Feature | 1.1, 1.6, 3.1 |
| 25 | F-018 — Webhooks | Feature | 1.1, 1.6, 1.7, 1.8 |
| 26 | F-019 — Data Export | Feature | 1.1, 1.6 |
| 27 | F-020 — Team Collaboration | Feature (Planned) | 1.1 |
| 28 | F-101 — Legacy v1 | Feature (Deprecated) | 1.1 |
| 29 | Frontend App | Module | 1.2, 3.9, 4.1 |
| 30 | Middleware | Module | 1.2, 3.10, 4.1, 5.1 |
| 31 | Notification Service | Service | 1.3, 3.6, 4.1, 4.2 |
| 32 | Orders Service | Service | 1.3, 3.4, 4.1, 4.2 |
| 33 | Org Service | Service | 1.3, 4.1, 4.2 |
| 34 | Reports Service | Service | 1.3, 4.1, 4.2 |
| 35 | Search Service | Service | 1.3, 3.8, 4.1, 4.2 |
| 36 | Storage Service | Service | 1.3, 3.5, 4.1, 4.2 |
| 37 | Webhooks Service | Service | 1.3, 4.1, 4.2 |

# Business Rules Catalog

## User Management Rules

### BR-001: Email Uniqueness
- **Description**: No two accounts may share the same email address. Email comparison is case-insensitive and trimmed before comparison.
- **Category**: Data Integrity
- **Enforcement Point**: Auth Service — User Registration handler (POST /auth/register).
- **Last Verified**: Not yet verified.
- **Exceptions**: System accounts (support@, noreply@) are reserved and cannot be registered.

### BR-002: Password Strength
- **Description**: Passwords must be at least 8 characters, contain one uppercase letter, one lowercase letter, one digit, and one special character.
- **Category**: Security
- **Enforcement Point**: Auth Service — Zod schema validation in registration and password reset flows.
- **Last Verified**: Not yet verified.

### BR-003: Account Lockout
- **Description**: After 5 consecutive failed login attempts, the account is locked for 15 minutes. Lockout counter resets on successful login or after the lockout period expires.
- **Category**: Security
- **Enforcement Point**: Auth Service — Login handler, Redis-based attempt counter.
- **Last Verified**: Not yet verified.

### BR-004: Session Expiry
- **Description**: Access tokens expire after 15 minutes. Refresh tokens expire after 7 days. Refresh tokens are single-use and rotated on each refresh.
- **Category**: Security
- **Enforcement Point**: Auth Service — Token generation and validation middleware.
- **Last Verified**: Not yet verified.

### BR-005: Email Verification
- **Description**: New accounts must verify their email within 24 hours of registration. Unverified accounts cannot access protected resources beyond profile setup.
- **Category**: Compliance
- **Enforcement Point**: API Gateway — middleware checks email_verified flag.
- **Last Verified**: Not yet verified.

### BR-006: Admin Invitation
- **Description**: Admin accounts can only be created through invitation by an existing admin. Self-registration as admin is prohibited.
- **Category**: Access Control
- **Enforcement Point**: Admin Panel — invitation endpoint checks invoker's role.
- **Last Verified**: Not yet verified.

## Order Management Rules

### BR-007: Order Total Minimum
- **Description**: Order total must be at least $5.00 before tax and shipping. Orders below this threshold are rejected.
- **Category**: Business Policy
- **Enforcement Point**: API Service — Order creation handler.
- **Last Verified**: Not yet verified.

### BR-008: Order Total Maximum
- **Description**: Single order total cannot exceed $50,000. Orders above this require manual approval from a finance admin.
- **Category**: Risk Management
- **Enforcement Point**: API Service — Order creation handler; flags for approval if exceeded.
- **Last Verified**: Not yet verified.

### BR-009: Inventory Reservation
- **Description**: When an order is placed, inventory is reserved for 30 minutes. If payment is not confirmed within that window, the reservation is released.
- **Category**: Data Integrity
- **Enforcement Point**: API Service — Order placement saga, Redis reservation with TTL.
- **Last Verified**: Not yet verified.

### BR-010: Cancellation Window
- **Description**: Orders can be cancelled without penalty within 1 hour of placement. After that, cancellation requires admin approval and may incur a fee.
- **Category**: Business Policy
- **Enforcement Point**: API Service — Order cancellation handler.
- **Last Verified**: Not yet verified.

### BR-011: Refund Policy
- **Description**: Refunds are processed to the original payment method within 5-10 business days. Partial refunds are allowed for multi-item orders.
- **Category**: Compliance
- **Enforcement Point**: Payment Worker — refund job logic.
- **Last Verified**: Not yet verified.

## Product Management Rules

### BR-012: SKU Uniqueness
- **Description**: Every product variant must have a unique SKU. SKUs are alphanumeric, 8-20 characters, and cannot be changed after creation.
- **Category**: Data Integrity
- **Enforcement Point**: API Service — Product creation/update handler.
- **Last Verified**: Not yet verified.

### BR-013: Pricing Rules
- **Description**: List price must be greater than cost price. Sale price must be less than or equal to list price. Prices are stored in cents (integer) to avoid floating-point issues.
- **Category**: Data Integrity
- **Enforcement Point**: API Service — Product creation/update handler, Prisma schema validation.
- **Last Verified**: Not yet verified.

### BR-014: Product Visibility
- **Description**: Products without inventory are automatically set to "out of stock" visibility. Products with negative inventory are set to "hidden" until inventory is corrected.
- **Category**: Business Policy
- **Enforcement Point**: Background Worker — periodic inventory sync job.
- **Last Verified**: Not yet verified.

## Discount Rules

### BR-015: Single Discount
- **Description**: Only one discount can be applied per order. Stacking discounts is not allowed.
- **Category**: Business Policy
- **Enforcement Point**: API Service — Order calculation logic.
- **Last Verified**: Not yet verified.

### BR-016: Discount Expiry
- **Description**: Discount codes must have an expiry date. Expired codes are rejected with a specific error message.
- **Category**: Business Policy
- **Enforcement Point**: API Service — Discount validation middleware.
- **Last Verified**: Not yet verified.

### BR-017: Discount Usage Limit
- **Description**: Discount codes can have a maximum usage limit. Once reached, the code is disabled automatically.
- **Category**: Business Policy
- **Enforcement Point**: API Service — Discount usage counter, checked before application.
- **Last Verified**: Not yet verified.

## Shipping Rules

### BR-018: Address Validation
- **Description**: Shipping addresses must pass basic validation: non-empty fields, valid postal code format, country in supported list.
- **Category**: Data Integrity
- **Enforcement Point**: API Service — Address validation middleware.
- **Last Verified**: Not yet verified.

### BR-019: Shipping Method Availability
- **Description**: Available shipping methods depend on destination country, order weight, and order value. Free shipping applies to orders over $100.
- **Category**: Business Policy
- **Enforcement Point**: API Service — Shipping calculation service.
- **Last Verified**: Not yet verified.

### BR-020: Tracking Requirement
- **Description**: All shipped orders must have a tracking number recorded within 24 hours of shipment. Orders without tracking after 24 hours trigger an alert.
- **Category**: Compliance
- **Enforcement Point**: Background Worker — scheduled job checks tracking status.
- **Last Verified**: Not yet verified.

## Audit & Compliance Rules

### BR-021: Audit Trail
- **Description**: All mutating operations on orders, users, and products must be recorded in the audit log with timestamp, actor, action, and before/after state.
- **Category**: Compliance
- **Enforcement Point**: Database triggers + middleware layer.
- **Last Verified**: Not yet verified.

### BR-022: Data Retention
- **Description**: User personal data is retained for the duration of the account plus 90 days after deletion. Audit logs are retained for 7 years.
- **Category**: Compliance
- **Enforcement Point**: Background Worker — data cleanup job.
- **Last Verified**: Not yet verified.

### BR-023: PII Masking
- **Description**: Personally Identifiable Information (email, phone, address) must be masked in all logs, error reports, and customer support interfaces.
- **Category**: Compliance
- **Enforcement Point**: Logger middleware, support tool frontend.
- **Last Verified**: Not yet verified.

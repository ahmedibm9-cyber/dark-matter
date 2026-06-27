# Business Rules

> This document catalogs every business rule in the system. Business rules encode the policies, constraints, and logic that define how the business operates. They are the most critical part of the system to get right, and they must be traceable from source (regulation, policy, stakeholder decision) through implementation and tests.

---

## 1. Business Rules Documentation Standards

### What Is a Business Rule?

A business rule is a statement that defines or constrains some aspect of the business. It is intended to assert business structure or to control or influence business behavior. Business rules are:

- **Atomic:** They state a single fact or constraint.
- **Declarative:** They state what must be, not how to enforce it.
- **Independent:** They exist regardless of the software system.
- **Stable:** They change only when the business changes, not when software changes.

### When to Document a Business Rule

Document a business rule when:
- It is a regulatory or compliance requirement
- It affects pricing, billing, or financial calculations
- It controls access to resources or data
- It validates critical data (health, safety, legal)
- It defines workflow transitions or state machines
- It has been a source of bugs or confusion in the past
- It is explicitly requested by stakeholders

### Business Rule Template

Each business rule follows this structure:

```markdown
### BR-[XXX]: [Rule Name]

| Attribute | Value |
|---|---|
| ID | BR-[XXX] |
| Version | [MAJOR.MINOR] |
| Status | [Draft / Active / Deprecated / Superseded] |
| Category | [Pricing / Access / Validation / Workflow / Compliance / Calculation] |
| Source | [REGULATION / STAKEHOLDER / POLICY_DOC / PRODUCT_DECISION] |
| Effective Date | [DATE] |
| Expiry Date | [DATE or N/A] |

**Statement:** [A clear, unambiguous statement of the rule.]

**Rationale:** [Why this rule exists — the business value, risk mitigated, or regulation satisfied.]

**Applicability:** [Which users, products, regions, or contexts this rule applies to.]

**Conditions:**
- [Condition 1: when this rule is triggered]
- [Condition 2: prerequisites]
- [Condition 3: exceptions]

**Action:**
- [What happens when the rule applies]

**Example(s):**
- [Positive example: scenario where rule is applied correctly]
- [Negative example: scenario that violates the rule]

**Implementation Details:**
- **Implemented In:** [Module / Service / File]
- **Enforcement Point:** [Input validation / Database constraint / Business logic / API gateway]
- **Configuration:** [Environment variables, feature flags, or config values used]
- **Related Code:** [Link to source file and line number]

**Test Coverage:**
- **Unit Test:** [Test file and test name]
- **Integration Test:** [Test file and test name]
- **Last Verified:** [DATE]
- **Verified By:** [NAME]

**Change History:**
| Date | Change | Reason | Author |
|---|---|---|---|
| [DATE] | Initial creation | Rule established | [NAME] |
| [DATE] | [Description of change] | [Why changed] | [NAME] |

**Related Rules:** [BR-XXX, BR-YYY — rules that depend on or conflict with this one]
```

---

## 2. Rule Categorization

### Categories

| Category | Description | Examples | Stability |
|---|---|---|---|
| **Pricing** | Rules that determine how much something costs | Discounts, tax rates, currency conversion, fee calculations | Medium — changes with promotions |
| **Access** | Rules that control who can do what | Role permissions, data visibility, feature gating | Low — rarely changes |
| **Validation** | Rules that determine what data is acceptable | Required fields, format constraints, business logic checks | Medium — evolves with product |
| **Workflow** | Rules that control state transitions | Order status flow, approval chains, escalation paths | Low — stable process flows |
| **Compliance** | Rules required by law or regulation | Data retention, consent requirements, audit logging | Very Low — changes with regulation |
| **Calculation** | Rules for deriving values from other values | Score calculation, risk assessment, eligibility scores | Medium — refined over time |

### Priority Levels

| Priority | Definition | Action on Violation |
|---|---|---|
| Critical | Regulatory or safety issue, financial impact | Block operation, alert immediately |
| High | Significant business impact, user-facing | Block operation, return error |
| Medium | Process impact, internal | Warn, log, or soft-block |
| Low | Preference, cosmetic | Log, no action |

---

## 3. Business Rules Catalog

### 3.1 Pricing Rules

---

#### BR-001: Tax Calculation Based on Jurisdiction

| Attribute | Value |
|---|---|
| ID | BR-001 |
| Status | Active |
| Category | Pricing |
| Source | Tax regulation per jurisdiction |
| Effective Date | 2024-01-01 |
| Expiry Date | N/A (updated as tax rates change) |

**Statement:** Sales tax is calculated based on the shipping address (not billing address), using the tax rate applicable in that jurisdiction.

**Rationale:** Tax laws require that sales tax be collected based on where the product is delivered, not where the buyer is registered.

**Applicability:** All orders shipped to addresses in jurisdictions with sales tax.

**Conditions:**
- Shipping address is required
- Tax rate is looked up from tax rate table by country/state/postal code
- Digital goods may have different tax rules (see BR-002)

**Action:**
- Look up tax rate by shipping address jurisdiction
- Apply rate to taxable subtotal (excluding shipping if not taxable)
- Add tax amount to order total

**Examples:**
- Positive: Shipping to New York, NY 10001 -> NY state tax 4% + NYC tax 4.5% = 8.5%
- Negative: Shipping to Portland, OR -> 0% (Oregon has no sales tax)

**Implementation Details:**
- Enforced in: `OrderPricingService.calculateTax()`
- Configuration: `TAX_RATE_TABLE_URL`, `TAX_PROVIDER_API_KEY`

**Test Coverage:**
- Unit test: `OrderPricingService.test.ts (should apply correct tax for NY address)`
- Integration test: `tax-integration.test.ts`

**Related Rules:** BR-002 (Digital goods tax treatment)

---

#### BR-002: Digital Goods Tax Exemption

| Attribute | Value |
|---|---|
| ID | BR-002 |
| Status | Active |
| Category | Pricing |
| Source | Tax regulation per jurisdiction |
| Effective Date | 2024-01-01 |

**Statement:** Digital goods (eBooks, software downloads, online courses) are exempt from sales tax in jurisdictions where digital goods are not taxable.

**Rationale:** Many jurisdictions do not tax digital goods, or tax them at a different rate than physical goods.

**Applicability:** Products flagged as `product_type = digital` in the product catalog.

**Conditions:**
- Product type is `digital`
- Jurisdiction's digital goods tax policy is checked
- Some jurisdictions still tax digital goods

**Action:**
- Skip sales tax for digital goods in exempt jurisdictions
- Apply digital goods tax rate in non-exempt jurisdictions

**Implementation Details:**
- Enforced in: `TaxCalculator`
- Configuration: `DIGITAL_GOODS_TAX_JURISDICTIONS` (list of jurisdictions that tax digital goods)

---

#### BR-003: Coupon Code — Single Use Per Customer

| Attribute | Value |
|---|---|
| ID | BR-003 |
| Status | Active |
| Category | Pricing |
| Source | Marketing policy |

**Statement:** A coupon code can only be used once per customer account. If a customer has already used a coupon code, attempting to use it again will result in an error.

**Rationale:** Prevents abuse of promotional codes and ensures fair distribution of discounts.

**Conditions:**
- Customer is logged in
- Coupon code is valid and active
- Coupon code usage limit is not exceeded globally
- Coupon code has not been used by this customer before

**Action:**
- Record coupon usage against customer ID
- Decline coupon if already used by this customer
- Return error: "Coupon code already redeemed"

**Implementation Details:**
- Enforced in: `CouponService.redeemCoupon()`
- Database: `coupon_redemptions` table with unique constraint on `(coupon_id, user_id)`

---

#### BR-004: Minimum Order Amount

| Attribute | Value |
|---|---|
| ID | BR-004 |
| Status | Active |
| Category | Validation |
| Source | Business operations policy |

**Statement:** Orders must have a minimum subtotal of $10.00 before applicable discounts and after applying coupon codes. Orders below this threshold cannot be placed.

**Rationale:** Ensures that transaction fees do not erode profit margins on small orders.

**Conditions:**
- Subtotal is calculated after all discounts
- Shipping costs are not counted toward minimum

**Action:**
- If subtotal < $10.00, show error: "Minimum order amount is $10.00"
- Block order placement

---

### 3.2 Access Rules

---

#### BR-010: Admin Access — Product Management

| Attribute | Value |
|---|---|
| ID | BR-010 |
| Status | Active |
| Category | Access |
| Source | Product team policy |

**Statement:** Only users with the `admin` or `product_manager` role can create, update, or delete products. Users with the `viewer` role can only read products.

**Rationale:** Prevents unauthorized changes to the product catalog, which could result in incorrect pricing, inventory issues, or regulatory violations.

**Conditions:**
- User is authenticated
- Operation is create, update, or delete on Product resource

**Action:**
- If role is `admin` or `product_manager`: allow operation
- If role is `viewer` or lower: return 403 Forbidden

**Implementation Details:**
- Enforced in: API middleware `requireRole('admin', 'product_manager')`
- Test: `authorization.test.ts (should block viewer from deleting product)`

---

#### BR-011: Data Visibility — Users Can Only See Their Own Data

| Attribute | Value |
|---|---|
| ID | BR-011 |
| Status | Active |
| Category | Access |
| Source | Privacy policy, GDPR |

**Statement:** A regular user can only view, edit, or delete their own account data and resources owned by their account. Admin users can view all data but must have a legitimate business reason to access it.

**Rationale:** GDPR right to privacy, data minimization principle, and general security best practice.

**Conditions:**
- Regular user requests access to a resource that has an owner
- Resource owner ID does not match requesting user ID

**Action:**
- Regular user: return 404 (not revealing existence of other user's data)
- Admin user: allow access, log access event

**Implementation Details:**
- Enforced in: Repository layer — queries filter by `user_id = :currentUserId`
- Audit: All admin access to user data is logged

---

### 3.3 Validation Rules

---

#### BR-020: Email Format Validation

| Attribute | Value |
|---|---|
| ID | BR-020 |
| Status | Active |
| Category | Validation |
| Source | RFC 5321, RFC 5322 |

**Statement:** Email addresses must conform to a valid format: `local-part@domain.tld`. The local part may contain alphanumeric characters, periods, hyphens, underscores, and plus signs. The domain must have at least one period with a valid TLD.

**Rationale:** Ensures that email addresses are syntactically valid before sending communications or using as login identifiers.

**Conditions:**
- Email is provided during registration, profile update, or password reset
- Email is not blank

**Action:**
- Validate against RFC-compliant regex
- If invalid: return `ValidationError` with field-level message

---

#### BR-021: Password Strength Requirements

| Attribute | Value |
|---|---|
| ID | BR-021 |
| Status | Active |
| Category | Validation |
| Source | Security policy |
| Effective Date | 2024-01-01 |

**Statement:** Passwords must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.

**Rationale:** Industry best practice (NIST SP 800-63B) for password strength to protect user accounts from brute force and credential stuffing attacks.

**Conditions:**
- Password is provided during registration or password change

**Action:**
- Validate length >= 8
- Validate at least 1 uppercase (A-Z)
- Validate at least 1 lowercase (a-z)
- Validate at least 1 digit (0-9)
- Validate at least 1 special character (!@#$%^&*()_+-=[]{}|;':\",./<>?)
- If invalid: return field-level error with specific criteria not met

---

### 3.4 Workflow Rules

---

#### BR-030: Order Status State Machine

| Attribute | Value |
|---|---|
| ID | BR-030 |
| Status | Active |
| Category | Workflow |
| Source | Operations policy |

**Statement:** Orders follow a defined state machine:
- `pending` -> `confirmed` -> `processing` -> `shipped` -> `delivered`
- `pending` -> `cancelled` (by user before confirmation)
- `confirmed` -> `cancelled` (by admin only)
- `shipped` -> `returned` (initiated by user, approved by admin)

Transitions not listed in this state machine are invalid and will be rejected.

**Rationale:** Ensures consistent order lifecycle management and prevents invalid state transitions that could lead to incorrect inventory, billing, or fulfillment actions.

**Applicability:** All orders.

**State Machine Diagram (Text-Based):**

```
                    ┌──────────┐
                    │ Pending  │
                    └────┬─────┘
                 ┌───────┼────────┐
                 │       │        │
                 ▼       ▼        ▼
            ┌────────┐ ┌────────────┐ ┌───────────┐
            │Confirmed│ │ Cancelled  │ │ (Expired) │
            └────┬────┘ └────────────┘ └───────────┘
                 │
                 ▼
            ┌──────────┐
            │Processing│
            └────┬─────┘
                 │
                 ▼
            ┌────────┐
            │ Shipped│
            └────┬───┘
              ┌──┴───┐
              │      │
              ▼      ▼
         ┌────────┐ ┌────────┐
         │Delivered│ │Returned│
         └────────┘ └────────┘
```

**Valid Transitions:**

| From | To | Allowed By | Conditions |
|---|---|---|---|
| pending | confirmed | System | Payment successful |
| pending | cancelled | User | Before payment confirmed |
| pending | expired | System | Payment timeout (30 min) |
| confirmed | processing | Admin | Inventory verified |
| confirmed | cancelled | Admin | Reason required |
| processing | shipped | Admin / System | Handoff to carrier |
| shipped | delivered | System | Carrier confirms delivery |
| shipped | returned | Admin | Return request approved |
| delivered | returned | Admin | Return within 30 days, approved |

**Invalid Transitions (Examples):**
- pending -> delivered (skipping confirmed and shipped)
- cancelled -> confirmed (already cancelled)
- delivered -> cancelled (delivered orders can only be returned)

**Implementation Details:**
- Enforced in: `OrderStateMachine` (abstracted from domain entity)
- Pattern: State pattern or enum with transition map
- Test: `OrderStateMachine.test.ts`

---

#### BR-031: Payment Retry Limit

| Attribute | Value |
|---|---|
| ID | BR-031 |
| Status | Active |
| Category | Workflow |
| Source | Operations policy, fraud prevention |

**Statement:** A failed payment can be retried up to 3 times. After 3 failed attempts, the order is cancelled and the user must create a new order.

**Rationale:** Prevents indefinite retries that could result in multiple charges, user confusion, or fraud attempts.

**Conditions:**
- Payment attempt fails (declined, timeout, error)
- Payment retry count is tracked per order

**Action:**
- If retry count < 3: allow retry, increment counter, notify user
- If retry count >= 3: cancel order, notify user, release inventory

---

### 3.5 Compliance Rules

---

#### BR-040: GDPR Data Retention — User Data Deletion

| Attribute | Value |
|---|---|
| ID | BR-040 |
| Status | Active |
| Category | Compliance |
| Source | GDPR Article 17, Right to Erasure |
| Effective Date | 2024-01-01 |

**Statement:** Upon receiving a verified account deletion request, all personal data must be removed within 30 days. Data required for legal or tax purposes (e.g., order history for 7 years) must be anonymized rather than deleted.

**Rationale:** Compliance with GDPR right to erasure (Article 17), while preserving data required by other regulations (tax, accounting).

**Applicability:** All users with accounts in the EU/EEA, or any user who requests deletion regardless of location (company policy).

**Conditions:**
- Deletion request is verified (user authenticated)
- Account has no pending financial obligations
- Account has no legal holds

**Action:**
- Anonymize PII fields in user record: name = [deleted], email = [UUID]@deleted.example.com
- Remove profile data, preferences, session data
- Retain order records with anonymized user reference
- Cancel active subscriptions
- Log deletion event for compliance audit
- Send confirmation email

**Implementation Details:**
- Enforced in: `AccountDeletionService`
- Last verified: 2024-06-01

---

#### BR-041: Audit Logging Requirement

| Attribute | Value |
|---|---|
| ID | BR-041 |
| Status | Active |
| Category | Compliance |
| Source | SOC2, PCI-DSS |

**Statement:** All access to sensitive data (PII, payment tokens, user credentials) and all administrative actions (role changes, data modifications, configuration changes) must be logged with: actor ID, action, resource type, resource ID, timestamp, IP address, and outcome (success/failure).

**Rationale:** SOC2 requirement for audit trails. Enables security incident investigation and compliance reporting.

**Applicability:** All system components that access or modify sensitive data.

**Action:**
- Log before and after values for modifications
- Logs are immutable (append-only)
- Logs retained for 1 year minimum
- Logs are accessible only to auditors and security team

---

### 3.6 Calculation Rules

---

#### BR-050: Order Total Calculation

| Attribute | Value |
|---|---|
| ID | BR-050 |
| Status | Active |
| Category | Calculation |
| Source | Finance policy |

**Statement:** Order total is calculated as: `subtotal + shipping_cost + tax - discount`. Where subtotal is `sum(quantity * unit_price)` for all order items, and discount is calculated from coupon code rules (percentage or fixed amount).

**Rationale:** Standard e-commerce calculation that matches accounting and tax reporting requirements.

**Conditions:**
- All order items must have a valid unit price
- Tax and shipping must be calculated before display

**Action:**

```
order_total = 0

for each item in order_items:
    subtotal += item.quantity * item.unit_price

shipping = calculate_shipping(order)
tax = calculate_tax(order, subtotal)
discount = calculate_discount(order, subtotal)

order_total = subtotal + shipping + tax - discount
```

**Implementation Details:**
- Enforced in: `OrderPricingService.calculateOrderTotal()`
- Precision: All monetary values stored as DECIMAL(10, 2), rounded to nearest cent
- Rounding: Half-up rounding applied at the final step only

---

#### BR-051: Loyalty Points Calculation

| Attribute | Value |
|---|---|
| ID | BR-051 |
| Status | Active |
| Category | Calculation |
| Source | Marketing policy |

**Statement:** Customers earn 1 loyalty point for every $1 spent on physical goods (excluding tax and shipping). Digital goods earn 0.5 points per $1 spent. Points expire 12 months after the date they were earned.

**Rationale:** Encourages repeat purchases of physical goods while accounting for the lower margin on digital goods.

**Conditions:**
- Order status is `delivered`
- Points calculated on subtotal (excluding tax, shipping, discounts)

**Action:**
- For physical goods: `points = round_down(subtotal_physical)`
- For digital goods: `points = round_down(subtotal_digital * 0.5)`
- Total points = sum of physical and digital points
- Points credited to account when order is delivered
- Points have 12-month expiry from credit date

---

## 4. Rules Engine Approach

### When to Use a Rules Engine

A rules engine (e.g., Drools, EasyRules, JSON-based rule engine) is considered when:

1. **Volume of rules exceeds 50** and they change frequently.
2. **Non-technical stakeholders** need to author or review rules.
3. **Rules have complex dependencies** or conflict resolution needs.
4. **Audit requirements** demand rule versioning and traceability at runtime.

### Current Approach

**For this project, business rules are implemented in code** (not a rules engine) because:

- The expected number of business rules is manageable (< 50).
- Rules change slowly (most are tied to regulation or stable business policy).
- Rules benefit from type safety, testability, and IDE support.
- No non-technical stakeholders need direct rule authoring.

If a rules engine becomes necessary in the future, the transition path is:

1. Extract rules into a centralized `BusinessRules` module (already done structurally).
2. Replace inline logic with a JSON-based rule definition format.
3. Integrate a rules engine under the same interface abstraction.

### Rule Abstraction Layer

Even without a rules engine, all business rules are abstracted behind a consistent interface:

```typescript
interface BusinessRule<TContext, TResult> {
  id: string;
  evaluate(context: TContext): RuleResult<TResult>;
}

interface RuleResult<T> {
  passed: boolean;
  value?: T;
  reason?: string;
}
```

This allows future migration to a rules engine without changing calling code.

---

## 5. Rules Versioning Strategy

### Version Numbering

Rules follow semantic versioning: `MAJOR.MINOR`

- **MAJOR:** Rule logic changes meaningfully — existing behavior changes.
- **MINOR:** Rule is clarified, conditions expanded, or new examples added — behavior unchanged.

### Rule Lifecycle

1. **Draft:** Rule is proposed, under review by stakeholders.
2. **Active:** Rule is approved and enforced in all environments.
3. **Deprecated:** Rule is phased out but still enforced for legacy cases.
4. **Superseded:** Rule is replaced by another rule (BR-XXX).

### Version Tracking

- Rules are versioned in the source of truth (this document).
- Rule implementation code is linked to this document via code comments.
- Rule changes go through the regular PR process.
- When a rule changes:
  - The version is bumped.
  - The change is logged in the rule's change history.
  - Affected tests are updated.
  - Affected stakeholders are notified.

---

## Appendix A: Business Rules Index

| ID | Name | Category | Priority | Status | Last Verified |
|---|---|---|---|---|---|
| BR-001 | Tax Calculation by Jurisdiction | Pricing | Critical | Active | 2024-06-01 |
| BR-002 | Digital Goods Tax Exemption | Pricing | High | Active | 2024-06-01 |
| BR-003 | Coupon Single Use Per Customer | Pricing | High | Active | 2024-06-01 |
| BR-004 | Minimum Order Amount | Pricing | Medium | Active | 2024-06-01 |
| BR-010 | Admin Access — Product Management | Access | Critical | Active | 2024-06-01 |
| BR-011 | Data Visibility — Own Data Only | Access | Critical | Active | 2024-06-01 |
| BR-020 | Email Format Validation | Validation | High | Active | 2024-06-01 |
| BR-021 | Password Strength Requirements | Validation | Critical | Active | 2024-06-01 |
| BR-030 | Order Status State Machine | Workflow | Critical | Active | 2024-06-01 |
| BR-031 | Payment Retry Limit | Workflow | High | Active | 2024-06-01 |
| BR-040 | GDPR Data Retention | Compliance | Critical | Active | 2024-06-15 |
| BR-041 | Audit Logging Requirement | Compliance | Critical | Active | 2024-06-15 |
| BR-050 | Order Total Calculation | Calculation | Critical | Active | 2024-06-01 |
| BR-051 | Loyalty Points Calculation | Calculation | Medium | Active | 2024-06-01 |

## Appendix B: Rule Verification Checklist

- [ ] Rule statement is unambiguous and testable
- [ ] Conditions are complete (no missing edge cases)
- [ ] Action is specific and implementable
- [ ] Examples cover both positive and negative cases
- [ ] Stakeholders have reviewed and approved
- [ ] Implementation exists and is linked
- [ ] Tests exist for positive case
- [ ] Tests exist for negative case (violation)
- [ ] Tests exist for edge cases
- [ ] Test results are passing
- [ ] Rule is indexed in the appendix

## Appendix C: Change Log

| Date | Author | Change | Rationale |
|---|---|---|---|
| [DATE] | [AUTHOR] | Initial creation | Business rules baseline |
| [DATE] | [AUTHOR] | [CHANGE] | [RATIONALE] |

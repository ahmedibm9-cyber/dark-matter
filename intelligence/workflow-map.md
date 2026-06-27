# Workflow Map

## User Registration
- **Trigger**: User submits registration form at /register
- **Steps**:
  1. Validate input (email, password, name) against BR-001, BR-002
  2. Check email uniqueness in database
  3. Hash password with bcrypt (cost factor 12)
  4. Insert user record with status `unverified`
  5. Generate email verification token (24h TTL)
  6. Send verification email via Background Worker
  7. Publish UserRegistered event
  8. Return 201 with user object (no token)
- **Output**: New user record, verification email sent
- **Failure Points**: Duplicate email (returns 409), weak password (returns 422), email send failure (retry 3x, then alert)

## User Login
- **Trigger**: User submits login form at /login
- **Steps**:
  1. Validate email and password presence
  2. Look up user by email
  3. Check BR-003 lockout status (Redis attempt counter)
  4. Compare password hash
  5. On failure: increment attempt counter; if >= 5, lock account 15min; return 401
  6. On success: reset attempt counter, generate access token (15min), generate refresh token (7d)
  7. Store refresh token hash in database
  8. Return tokens and user profile
- **Output**: Access token, refresh token, user profile
- **Failure Points**: Account locked (returns 423 with retry-after), invalid credentials (returns 401)

## Order Placement
- **Trigger**: User clicks "Place Order" from checkout page
- **Steps**:
  1. Validate cart is not empty and items are available
  2. Check BR-007 (min total) and BR-008 (max total)
  3. Validate BR-015 single discount rule and BR-016/017 discount rules
  4. Validate BR-018 shipping address
  5. Validate BR-019 shipping method availability
  6. Reserve inventory for all items (BR-009) with 30min TTL
  7. Calculate totals (subtotal, tax, shipping, grand total)
  8. Create Order record in `pending` status
  9. Create OrderItem records for each cart item
  10. Create Payment record in `pending` status
  11. Create Shipment record in `pending` status
  12. Decrement discount usage count if applicable
  13. Clear the user's cart
  14. Publish OrderPlaced event
  15. Trigger payment charge asynchronously via Background Worker
  16. Return 201 with order object
- **Output**: Order with all line items, payment pending
- **Failure Points**: Inventory insufficient (returns 409), discount expired (returns 422), payment gateway down (fallback to async retry)

## Payment Processing
- **Trigger**: OrderPlaced event consumed by Background Worker
- **Steps**:
  1. Retrieve order and payment records
  2. Determine payment method from order
  3. Call payment gateway (Stripe/PayPal)
  4. Gateway processes charge
  5. On success: update payment status to `captured`, update order status to `confirmed`, publish PaymentCaptured event
  6. On failure: update payment status to `failed`, keep order as `pending`, schedule retry (3 attempts), publish PaymentFailed event
  7. Log audit trail entry
- **Output**: Payment captured or scheduled for retry
- **Failure Points**: Gateway timeout (retry with exponential backoff), card declined (notify user), fraud detection (flag for review)

## Order Fulfillment
- **Trigger**: Order status changes to `confirmed`
- **Steps**:
  1. Fulfillment system receives notification
  2. Generate packing slip
  3. Warehouse team picks items from inventory
  4. Update inventory quantities (decrement actual stock)
  5. Package items and generate shipping label
  6. Assign tracking number (BR-020)
  7. Update shipment status to `labeled`
  8. Hand off to carrier
  9. Update shipment status to `pickedUp`
  10. Update order status to `shipped`
  11. Publish OrderShipped event
  12. Send tracking notification to buyer
- **Output**: Order shipped, tracking number available
- **Failure Points**: Inventory discrepancy (pause and audit), carrier API down (retry), label generation failed (manual intervention)

## Order Cancellation
- **Trigger**: User clicks "Cancel Order" or admin initiates cancellation
- **Steps**:
  1. Check order status — only `pending` or `confirmed` can be cancelled
  2. Check BR-010 cancellation window
  3. If within 1 hour of placement: proceed with automatic cancellation
  4. If outside 1 hour: require admin approval
  5. Release inventory reservations (BR-009 reversal)
  6. If payment was captured: initiate refund via BR-011
  7. Update order status to `cancelled`
  8. Publish OrderCancelled event
  9. Send cancellation confirmation email
- **Output**: Order cancelled, inventory released, refund initiated if applicable
- **Failure Points**: Order already shipped (reject cancellation), refund gateway error (manual processing)

## Product Lifecycle
- **Trigger**: Seller creates or updates a product
- **Steps**:
  1. Validate BR-012 SKU uniqueness
  2. Validate BR-013 pricing rules (list > cost, sale <= list)
  3. Create or update product record
  4. Create or update variants
  5. Initialize inventory records for new variants
  6. Publish ProductCreated or ProductUpdated event
  7. Trigger search index reindexing
  8. Evaluate BR-014 visibility rules
- **Output**: Product created/updated with variants and inventory
- **Failure Points**: SKU collision (returns 409), invalid pricing (returns 422), image upload failure (retry)

## Weekly Tech Debt Triage
- **Trigger**: Weekly checklist — every Monday
- **Steps**:
  1. Open technical-debt.md
  2. Review items with priority = HIGH
  3. Estimate effort for unestimated items
  4. Reassign owners if missing
  5. Promote items to active sprint if effort <= 3 story points
  6. Archive items marked as resolved
  7. Add new items identified during the week
  8. Update cost and effort estimates for existing items
  9. Commit updated technical-debt.md
- **Output**: Updated technical debt catalog
- **Failure Points**: None (advisory workflow)

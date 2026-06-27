# Known Bugs

## BUG-001: Cart Total Calculation Off by One Cent
- **Description**: When calculating cart totals, rounding errors cause the displayed total to be off by ±$0.01 in approximately 2% of carts. This occurs when line items have fractional cent amounts that are rounded differently at the cart level vs. the order level.
- **Severity**: LOW
- **Affected Component**: API Service — Cart calculation service
- **Steps to Reproduce**:
  1. Add 3 items with prices $9.99, $14.99, $24.99 to cart
  2. Apply a 15% discount
  3. Observe cart total vs. order total differ by $0.01
- **Workaround**: None. The final order total is correct; only the cart preview is affected.
- **Root Cause**: Rounding applied at line-item level uses different precision than the cart-level summation.
- **Fix ETA**: Next sprint (est. 2 days to fix, test, deploy)
- **Reported By**: QA team (2025-04-20)
- **Related**: None

## BUG-002: Session Not Invalidated on Password Change
- **Description**: When a user changes their password, existing sessions (other devices, browsers) remain valid. The user can continue to use old access tokens until they expire (15 minutes).
- **Severity**: MEDIUM
- **Affected Component**: Auth Service — Password change handler
- **Steps to Reproduce**:
  1. User logs in on two devices
  2. User changes password on device 1
  3. Device 2 continues to work for up to 15 minutes (until access token expires)
- **Workaround**: None. Users must manually log out of all devices.
- **Root Cause**: Password change handler does not invalidate the refresh token family or blacklist existing access tokens.
- **Fix ETA**: Current sprint (est. 1 day)
- **Reported By**: Security audit (2025-04-18)
- **Related**: BR-004, ADR-011

## BUG-003: Product Search Returns Deleted Products
- **Description**: Despite implementing soft delete (FAIL-002 fix), the search index still returns deleted products. The search index is not reindexed when a product is soft-deleted.
- **Severity**: MEDIUM
- **Affected Component**: Search Index — Product indexer
- **Steps to Reproduce**:
  1. Admin soft-deletes a product
  2. Search still shows the product in results
  3. Clicking the product returns 404
- **Workaround**: Manually trigger full reindex after bulk deletions.
- **Root Cause**: Search indexer only listens to ProductCreated and ProductUpdated events, not ProductDeleted.
- **Fix ETA**: Next sprint (est. 1 day)
- **Reported By**: QA team (2025-04-22)
- **Related**: FAIL-002

## BUG-004: Discount Code Case Sensitivity Mismatch
- **Description**: Discount codes are stored in their original case but compared case-sensitively. Users typing "SAVE20" vs "save20" get different results.
- **Severity**: LOW
- **Affected Component**: API Service — Discount validation
- **Steps to Reproduce**:
  1. Admin creates discount code "SAVE20"
  2. User enters "save20" at checkout
  3. Discount is not applied
- **Workaround**: Users must enter the exact case as created.
- **Root Cause**: Discount code lookup uses exact string comparison instead of case-insensitive comparison.
- **Fix ETA**: Backlog (est. 2 hours)
- **Reported By**: Customer support (2025-04-15)
- **Related**: None

## BUG-005: Admin Panel Pagination Resets on Filter
- **Description**: When viewing the orders list in the admin panel and applying a filter, pagination resets to page 1 even if the user was on page 3. This makes it tedious to browse filtered results across multiple pages.
- **Severity**: LOW
- **Affected Component**: Admin Panel — Order list component
- **Steps to Reproduce**:
  1. Navigate to Admin Panel > Orders > Page 3
  2. Apply a status filter (e.g., "Shipped")
  3. Page resets to 1
- **Workaround**: Manually navigate back to the desired page after filtering.
- **Root Cause**: Filter state and pagination state are managed independently without preserving page on filter change.
- **Fix ETA**: Backlog (est. 1 day)
- **Reported By**: Internal team (2025-04-10)
- **Related**: None

## BUG-006: Email Verification Link Expired Without Warning
- **Description**: When clicking an expired email verification link (after 24 hours), the user sees a generic error page without instructions on how to request a new verification email.
- **Severity**: LOW
- **Affected Component**: Auth Service — Email verification handler
- **Steps to Reproduce**:
  1. Register a new account
  2. Wait 24+ hours without verifying
  3. Click the verification link from the email
  4. See generic error
- **Workaround**: Contact support to resend verification email.
- **Root Cause**: No "resend verification" link on the error page. No token renewal flow.
- **Fix ETA**: Next sprint (est. 1 day)
- **Reported By**: Customer support (2025-04-12)
- **Related**: BR-005

## BUG-007: Shipping Cost Not Recalculated on Address Change
- **Description**: When a user changes their shipping address during checkout, the shipping cost is not recalculated until the page is manually refreshed. The displayed total shows the old shipping cost.
- **Severity**: LOW
- **Affected Component**: Web App — Checkout page
- **Steps to Reproduce**:
  1. Enter checkout with a domestic address (shows $5 shipping)
  2. Change address to an international address (should be $15 shipping)
  3. Total still shows $5 shipping
- **Workaround**: Refresh the page after changing address.
- **Root Cause**: Address change event does not trigger shipping recalculation. React Query cache for shipping rates is not invalidated.
- **Fix ETA**: Current sprint (est. 1 day)
- **Reported By**: QA team (2025-04-19)
- **Related**: BR-019

## BUG-008: Bulk Discount Not Working with Multi-Quantity Items
- **Description**: A discount that applies to "3 or more items" only counts unique line items, not total quantity. Adding 3 of the same item does not trigger the discount.
- **Severity**: MEDIUM
- **Affected Component**: API Service — Discount calculation
- **Steps to Reproduce**:
  1. Create discount: "Buy 3, get 10% off"
  2. Add 3 identical items to cart
  3. Discount is not applied
- **Workaround**: Add 3 different items instead of 3 of the same item.
- **Root Cause**: Discount threshold logic counts cart items by unique variant, not total quantity.
- **Fix ETA**: Next sprint (est. 2 days)
- **Reported By**: Customer support (2025-04-21)
- **Related**: BR-015

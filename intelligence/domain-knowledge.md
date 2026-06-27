# Domain Knowledge

## Business Domain
The system operates in the **e-commerce** domain, specifically a multi-vendor marketplace platform. It connects buyers with sellers, manages product listings, processes orders, handles payments, and coordinates shipping.

## Core Domain Concepts

### User
A person or entity that interacts with the system. Users have roles (buyer, seller, admin) that determine their permissions and capabilities.
- **Attributes**: id, email, name, role, emailVerified, createdAt, updatedAt, deletedAt (soft delete)
- **Relationships**: Has many Orders (as buyer), has many Products (as seller), has one Cart, has many Addresses

### Product
An item offered for sale on the marketplace. Products belong to a seller and are organized into categories.
- **Attributes**: id, sku, name, description, listPrice, costPrice, salePrice, status, categoryId, sellerId, createdAt, updatedAt
- **Variants**: Products can have variants (size, color) each with its own SKU and inventory.
- **Relationships**: Belongs to Seller (User), belongs to Category, has many Variants, has many Reviews, has Inventory records

### Variant
A specific version of a product distinguished by attributes like size, color, or material.
- **Attributes**: id, productId, sku, attributes (JSON), listPrice, costPrice, salePrice, status
- **Relationships**: Belongs to Product, has Inventory records

### Inventory
Tracks stock levels for each product variant.
- **Attributes**: id, variantId, quantity, reservedQuantity, availableQuantity, lowStockThreshold, updatedAt
- **Key Logic**: availableQuantity = quantity - reservedQuantity
- **Events**: LowStockWarning, OutOfStock, InventoryRestocked

### Category
A hierarchical classification for products. Categories can have parent-child relationships.
- **Attributes**: id, name, slug, description, parentId, sortOrder
- **Relationships**: Has many Products, belongs to parent Category

### Cart
A temporary collection of items a buyer intends to purchase. Carts expire after 30 days of inactivity.
- **Attributes**: id, userId, createdAt, updatedAt, expiresAt
- **Relationships**: Belongs to User, has many CartItems

### CartItem
A single line item within a cart.
- **Attributes**: id, cartId, variantId, quantity, unitPrice, createdAt
- **Relationships**: Belongs to Cart, belongs to Variant

### Order
A completed purchase transaction. Orders progress through several lifecycle states.
- **States**: pending, confirmed, processing, shipped, delivered, cancelled, refunded
- **Attributes**: id, userId, orderNumber, status, subtotal, taxTotal, shippingTotal, grandTotal, currency, notes, createdAt, updatedAt
- **Relationships**: Belongs to User, has many OrderItems, has one Payment, has one Shipment, has many StatusHistories

### OrderItem
An individual line item within an order.
- **Attributes**: id, orderId, variantId, quantity, unitPrice, lineTotal, createdAt
- **Relationships**: Belongs to Order, belongs to Variant

### Payment
A financial transaction for an order. Payments can be made via credit card, PayPal, or bank transfer.
- **Attributes**: id, orderId, method, status, amount, currency, transactionId, gatewayResponse, createdAt
- **States**: pending, authorized, captured, failed, refunded, partiallyRefunded
- **Relationships**: Belongs to Order

### Shipment
The physical delivery of an order to a buyer's address.
- **Attributes**: id, orderId, addressId, method, trackingNumber, carrier, status, estimatedDelivery, shippedAt, deliveredAt
- **States**: pending, labeled, pickedUp, inTransit, outForDelivery, delivered, failed
- **Relationships**: Belongs to Order, belongs to Address

### Discount
A promotional reduction in order price. Discounts can be percentage-based or fixed amount.
- **Attributes**: id, code, type (percentage/fixed), value, minOrderAmount, maxUsageCount, currentUsageCount, expiresAt, isActive
- **Relationships**: Can be applied to Orders

### Review
Feedback left by a buyer on a purchased product.
- **Attributes**: id, productId, userId, rating (1-5), title, body, isVerifiedPurchase, createdAt
- **Relationships**: Belongs to Product, belongs to User

### Address
A physical location associated with a user.
- **Attributes**: id, userId, label, firstName, lastName, line1, line2, city, state, postalCode, country, isDefault, createdAt
- **Relationships**: Belongs to User

### AuditLog
A record of all state-changing operations for compliance and debugging.
- **Attributes**: id, entityType, entityId, action, actorId, beforeState (JSONB), afterState (JSONB), ipAddress, userAgent, createdAt

## Ubiquitous Language

| Term | Definition | Used In |
|---|---|---|
| SKU | Stock Keeping Unit — unique identifier for a product variant | Product, Inventory |
| List Price | The standard selling price shown on the product page | Product, OrderItem |
| Sale Price | The discounted price if a sale is active | Product, OrderItem |
| Grand Total | The final amount charged to the buyer | Order |
| Line Total | quantity * unitPrice for an order item | OrderItem |
| Reservation | Temporarily holding inventory for an in-progress order | Inventory |
| Gateway | Third-party payment processor (Stripe, PayPal) | Payment |
| Chargeback | A dispute initiated by the buyer's bank against a payment | Payment |
| Fulfillment | The process of picking, packing, and shipping an order | Shipment |
| Marketplace | The platform connecting multiple sellers with buyers | System-wide |
| Soft Delete | Marking a record as deleted without removing it | User, Product |

## Entity Relationship Summary

```
User 1---* Order
User 1---* Address
User 1---* Product (as seller)
User 1---1 Cart
Cart 1---* CartItem
CartItem *---1 Variant
Product 1---* Variant
Product *---1 Category
Variant 1---1 Inventory
Variant 1---* OrderItem
Order 1---* OrderItem
Order 1---0..1 Payment
Order 1---0..1 Shipment
Order *---0..1 Discount
Order 1---* StatusHistory
Product 1---* Review
User 1---* Review
```

## Domain Events
- UserRegistered, UserEmailVerified, UserDeleted
- ProductCreated, ProductUpdated, ProductVisibilityChanged
- OrderPlaced, OrderConfirmed, OrderShipped, OrderDelivered, OrderCancelled, OrderRefunded
- PaymentAuthorized, PaymentCaptured, PaymentFailed, PaymentRefunded
- InventoryReserved, InventoryReleased, InventoryLow, InventoryOutOfStock
- ReviewSubmitted

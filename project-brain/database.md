# Database

> This document defines the database architecture, schema design principles, naming conventions, table definitions, migration strategy, and operational practices for the project.

---

## 1. Database Overview

### System Details

| Attribute | Value |
|---|---|
| Database Type | [PostgreSQL / MySQL / Microsoft SQL Server / MongoDB / etc.] |
| Version | [VERSION_NUMBER] |
| Hosting | [Self-hosted / AWS RDS / Azure SQL / GCP Cloud SQL / etc.] |
| Instance Class | [INSTANCE_TYPE] |
| Storage | [STORAGE_TYPE_AND_SIZE] |
| Connection Pool | [TOOL_AND_CONFIG] |
| Backend Driver | [DRIVER_LIBRARY] |
| ORM / Query Builder | [ORM_LIBRARY] |
| Migration Tool | [TOOL_NAME] |

### Connection Configuration

```ini
# Connection string format placeholder
DATABASE_URL=[PROTOCOL]://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE_NAME]
POOL_MIN=2
POOL_MAX=20
POOL_IDLE_TIMEOUT=30000
POOL_ACQUIRE_TIMEOUT=10000
SSL_MODE=require
```

### Environment-Specific Configuration

| Environment | Host | Port | DB Name | Pool Size | Backup Schedule |
|---|---|---|---|---|---|
| Development | localhost | 5432 | app_dev | 5 | None |
| Testing | test-db.local | 5432 | app_test | 10 | None |
| Staging | staging-db.internal | 5432 | app_staging | 15 | Daily |
| Production | prod-db.internal | 5432 | app_prod | 25 | Continuous + Daily |

---

## 2. Entity Relationship Overview

### High-Level Context Map

```ascii
┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │─────│  Order   │─────│  Payment │
└──────────┘     └──────────┘     └──────────┘
     │                │
     │                ▼
     │          ┌──────────┐     ┌──────────┐
     └──────────│  Address │     │  Product │
                └──────────┘     └──────────┘
                                       │
                                       ▼
                                  ┌──────────┐
                                  │ Category │
                                  └──────────┘
```

### ER Diagram (Text-Based)

```
 ┌──────────────────────┐
 │        User          │
 ├──────────────────────┤
 │ id: UUID [PK]        │──┐
 │ email: VARCHAR(255)  │  │  ┌──────────────────────┐
 │ password_hash: TEXT  │  │  │       Order          │
 │ name: VARCHAR(100)   │  ├──│──────────────────────│
 │ status: ENUM         │  │  │ id: UUID [PK]        │
 │ created_at: TIMESTAMP│  │  │ user_id: UUID [FK]   │──┐
 │ updated_at: TIMESTAMP│  │  │ status: ENUM          │  │
 └──────────────────────┘  │  │ total: DECIMAL(10,2)  │  │
                           │  │ currency: VARCHAR(3)  │  │
 ┌──────────────────────┐  │  │ shipping_address_id   │  │
 │     UserSession      │  │  │ : UUID [FK]           │  │
 ├──────────────────────┤  │  │ created_at: TIMESTAMP │  │
 │ id: UUID [PK]        │  │  │ updated_at: TIMESTAMP │  │
 │ user_id: UUID [FK]   │──┘  └──────────────────────┘  │
 │ token: TEXT          │                                │
 │ expires_at: TIMESTAMP│     ┌──────────────────────┐   │
 │ created_at: TIMESTAMP│     │     OrderItem        │   │
 └──────────────────────┘     ├──────────────────────┤   │
                              │ id: UUID [PK]        │   │
 ┌──────────────────────┐     │ order_id: UUID [FK]  │───┘
 │       Product        │     │ product_id: UUID [FK]│──┐
 ├──────────────────────┤     │ quantity: INT        │  │
 │ id: UUID [PK]        │──┐  │ unit_price: DECIMAL  │  │
 │ name: VARCHAR(255)   │  │  │ total: DECIMAL(10,2) │  │
 │ description: TEXT    │  │  └──────────────────────┘  │
 │ price: DECIMAL(10,2) │  │                           │
 │ currency: VARCHAR(3) │  │  ┌──────────────────────┐  │
 │ stock: INT           │  │  │     ProductReview    │  │
 │ category_id: UUID[FK]│  │  ├──────────────────────┤  │
 │ status: ENUM         │  │  │ id: UUID [PK]        │  │
 │ created_at: TIMESTAMP│  │  │ product_id: UUID[FK] │──┘
 └──────────────────────┘  │  │ user_id: UUID [FK]   │
                           │  │ rating: INT (1-5)    │
 ┌──────────────────────┐  │  │ title: VARCHAR(200)  │
 │      Category        │  │  │ body: TEXT           │
 ├──────────────────────┤  │  │ moderated: BOOLEAN   │
 │ id: UUID [PK]        │──┘  │ created_at: TIMESTAMP│
 │ name: VARCHAR(100)   │     └──────────────────────┘
 │ slug: VARCHAR(100)   │
 │ parent_id: UUID [FK] │──(self-referencing)
 │ sort_order: INT      │
 │ created_at: TIMESTAMP│
 └──────────────────────┘
```

---

## 3. Schema Design Principles

### Core Principles

1. **Normalization to 3NF:** Data is normalized to Third Normal Form unless there is a verified performance reason to denormalize. Denormalization decisions are documented with rationale and trade-offs.
2. **Surrogate Keys:** Every table uses UUID v4 as the primary key. Natural keys (email, slug) have unique constraints but are not used as PKs.
3. **Immutable Audit Columns:** Every table includes `created_at` (immutable) and `updated_at` (updated on change). These are managed by database triggers, not application code.
4. **Soft Deletes Preferred:** Data is soft-deleted with a `deleted_at` TIMESTAMP column rather than hard-deleted, unless privacy/compliance requires physical deletion.
5. **Explicit Constraints:** Every relationship is enforced with foreign key constraints. Every column has an explicit NOT NULL or NULL constraint. Default values are set at the schema level.
6. **Index Everything You Query:** Every column used in WHERE, JOIN, ORDER BY, or GROUP BY clauses is indexed. Composite indexes match query patterns exactly.
7. **No Business Logic in the Database:** Stored procedures, triggers, and functions are avoided unless required for performance or integrity that cannot be enforced at the application layer.
8. **Documented Deviations:** Every deviation from these principles is documented with a comment in the migration file and a rationale in this document.

---

## 4. Naming Conventions

### General Rules

- **Table names:** Lowercase, snake_case, plural (e.g., `users`, `order_items`, `product_reviews`)
- **Column names:** Lowercase, snake_case (e.g., `first_name`, `created_at`, `password_hash`)
- **Primary keys:** `id`
- **Foreign keys:** `[referenced_table_singular]_id` (e.g., `user_id`, `order_id`)
- **Join tables:** `[table_a]_[table_b]` in alphabetical order (e.g., `product_categories`, `user_roles`)
- **Indexes:** `idx_[table]_[column(s)]` (e.g., `idx_users_email`, `idx_orders_user_id_created_at`)
- **Unique constraints:** `uq_[table]_[column(s)]` (e.g., `uq_users_email`)
- **Check constraints:** `ck_[table]_[description]` (e.g., `ck_users_age_positive`)

### Data Types

| Logical Type | Database Type | Notes |
|---|---|---|
| Identity (PK) | UUID | UUID v4, generated client-side or by DB |
| Short string | VARCHAR(50) | Names, codes, abbreviations |
| Medium string | VARCHAR(255) | Emails, titles, slugs |
| Long string | VARCHAR(2000) | Descriptions, notes |
| Text | TEXT | Unlimited length content |
| Integer | INT or BIGINT | BIGINT for counts that may exceed 2B |
| Decimal | DECIMAL(p, s) | Money: DECIMAL(10, 2) |
| Boolean | BOOLEAN | |
| Date | DATE | |
| Timestamp | TIMESTAMPTZ | Always with timezone |
| JSON | JSONB | PostgreSQL: prefer JSONB over JSON |
| Enum | ENUM or VARCHAR with CHECK | Prefer VARCHAR + CHECK for portability |
| IP Address | INET | PostgreSQL specific |
| Monetary | DECIMAL(10, 2) | Store in minor unit documentation |

---

## 5. Table Definitions

### Table: [table_name]

| Attribute | Value |
|---|---|
| Purpose | [What this table stores and why] |
| Estimated Row Count | [ESTIMATE] |
| Growth Rate | [PER_DAY / PER_MONTH] |
| Partitioning | [NONE / BY_DATE / BY_REGION] |
| Retention | [FOREVER / N_DAYS / N_MONTHS] |

#### Columns

| Column | Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | UUID | NO | gen_random_uuid() | PK | Primary key |
| [column] | [TYPE] | [YES/NO] | [DEFAULT] | [FK / UNIQUE / CHECK] | [DESCRIPTION] |
| [column] | [TYPE] | [YES/NO] | [DEFAULT] | [FK / UNIQUE / CHECK] | [DESCRIPTION] |
| [column] | [TYPE] | [YES/NO] | [DEFAULT] | [FK / UNIQUE / CHECK] | [DESCRIPTION] |
| created_at | TIMESTAMPTZ | NO | NOW() | | Row creation timestamp |
| updated_at | TIMESTAMPTZ | NO | NOW() | | Row last update timestamp |
| deleted_at | TIMESTAMPTZ | YES | NULL | | Soft delete timestamp |

#### Indexes

| Name | Type | Columns | Condition | Justification |
|---|---|---|---|---|
| idx_[table]_[col] | BTREE / UNIQUE / GIN | [column] | [WHERE clause if partial] | [Why this index exists] |
| idx_[table]_[col1_col2] | BTREE | [col1, col2] | | Composite for common query pattern |

#### Relationships

| Parent Table | Relationship | Column | On Delete | On Update |
|---|---|---|---|---|
| [parent_table] | [ONE_TO_MANY / MANY_TO_ONE] | [column] | [CASCADE / SET NULL / RESTRICT] | [CASCADE / RESTRICT] |
| [parent_table] | [MANY_TO_MANY via table] | [column] | [CASCADE / SET NULL / RESTRICT] | [CASCADE / RESTRICT] |

---

### Table: users

| Attribute | Value |
|---|---|
| Purpose | Core user accounts and authentication |
| Estimated Row Count | 1,000,000 |
| Growth Rate | 5,000 per month |
| Partitioning | None |
| Retention | Forever (anonymized on account deletion) |

#### Columns

| Column | Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | UUID | NO | gen_random_uuid() | PK | Primary key |
| email | VARCHAR(255) | NO | | UNIQUE, NOT NULL | User email address (login ID) |
| password_hash | VARCHAR(255) | NO | | NOT NULL | bcrypt hash of password |
| name | VARCHAR(100) | NO | | NOT NULL | Display name |
| avatar_url | VARCHAR(500) | YES | NULL | | Profile picture URL |
| role | VARCHAR(20) | NO | 'user' | CHECK(role IN ('user','admin','moderator')) | Authorization role |
| status | VARCHAR(20) | NO | 'active' | CHECK(status IN ('active','suspended','disabled')) | Account status |
| email_verified_at | TIMESTAMPTZ | YES | NULL | | When email was verified |
| last_login_at | TIMESTAMPTZ | YES | NULL | | Last successful login |
| metadata | JSONB | YES | '{}' | | Flexible metadata for custom fields |
| created_at | TIMESTAMPTZ | NO | NOW() | | Row creation timestamp |
| updated_at | TIMESTAMPTZ | NO | NOW() | | Row last update timestamp |
| deleted_at | TIMESTAMPTZ | YES | NULL | | Soft delete timestamp |

#### Indexes

| Name | Type | Columns | Condition | Justification |
|---|---|---|---|---|
| uq_users_email | UNIQUE BTREE | email | | Login lookup |
| idx_users_status | BTREE | status | | Admin filtering by status |
| idx_users_created_at | BTREE | created_at | | Analytics queries |
| idx_users_status_created | BTREE | status, created_at | | Reporting queries |

---

### Table: [table_name_2]

[Repeat the same structure for every table in the system]

---

## 6. Migration Strategy

### Migration Philosophy

- **All schema changes are code:** Migrations are version-controlled, reviewed, and tested like application code.
- **Forward-only:** Once a migration is applied to a shared environment, it is never modified. Fix issues with a new migration.
- **Backward compatible:** All migrations must be backward compatible with the current production code. Deploy code first, then migrate.
- **Repeatable and idempotent:** Migrations use IF NOT EXISTS / IF EXISTS patterns. Running a migration twice is safe.

### Migration Naming Convention

```
[YYYYMMDD]_[HHMMSS]_[short_description].sql
```

Example: `20240101_120000_create_users_table.sql`

### Migration Directory Structure

```
db/
  migrations/
    20240101_120000_create_users_table.sql
    20240101_121000_create_orders_table.sql
    20240102_090000_add_status_to_users.sql
    20240103_140000_create_index_orders_user_id.sql
  seeds/
    20240101_dev_seed.sql
    20240101_test_seed.sql
  scripts/
    migrate.sh
    rollback.sh
    seed.sh
```

### Migration Lifecycle

1. **Development:** Developer creates migration locally. Runs it against local database.
2. **Code Review:** Migration is reviewed for correctness, performance, and backward compatibility.
3. **CI:** Migration is applied to test database. Tests run against migrated schema.
4. **Staging:** Migration is applied to staging. Smoke tests verify no regressions.
5. **Production:** Migration is applied during maintenance window or via zero-downtime deployment.

### Zero-Downtime Migration Patterns

| Change Type | Safe Strategy | Notes |
|---|---|---|
| Add column (nullable) | Safe anytime | |
| Add column (not null with default) | Safe: add nullable, backfill, add NOT NULL | Three-step migration |
| Drop column | Safe: deploy code that stops using it, then drop | Two deployments |
| Rename column | Add new column, dual-write, backfill, deploy read-only new, drop old | Multi-step |
| Add index | CONCURRENTLY (PostgreSQL) | Avoids table lock |
| Drop index | Safe: queries will use other indexes or seq scan | Monitor performance |
| Change column type | Add new column, dual-write, backfill, swap | Multi-step |
| Split table | Create new table, dual-write, backfill, redirect reads | Multi-step |

### Rollback Strategy

- **Explicit rollback migrations** are written for every migration (in `db/rollbacks/` directory).
- Rollbacks are tested in CI alongside forward migrations.
- Rollback is a last resort. The preferred fix is a forward migration.

---

## 7. Query Patterns and Optimization

### Common Query Patterns

| Pattern | Description | Optimization Strategy |
|---|---|---|
| Point lookup | Fetch single row by PK | Primary key index |
| User-scoped list | Fetch user's entities by user_id | Composite index on (user_id, created_at) |
| Time-range scan | Fetch entities within date range | Index on timestamp column |
| Full-text search | Search across text columns | GIN index (PostgreSQL) / Elasticsearch |
| Aggregation | SUM, COUNT, AVG across large sets | Materialized views / read replicas |
| Pagination | Page through results | Keyset pagination (cursor-based) over offset-based |

### N+1 Query Prevention

- Use JOIN or batch loading (DataLoader pattern) for related entities.
- ORM: Eager load relationships that are always needed.
- API: Allow clients to specify includes via `?include=relation1,relation2`.
- Code review rule: Any N+1 pattern is a blocking review finding.

### Query Performance Targets

| Query Type | Target Latency (p50) | Target Latency (p99) | Target Latency (p999) |
|---|---|---|---|
| Point lookup (by PK) | < 5ms | < 20ms | < 50ms |
| Simple list (indexed) | < 20ms | < 100ms | < 500ms |
| Complex join (indexed) | < 100ms | < 500ms | < 2000ms |
| Full-text search | < 200ms | < 1000ms | < 5000ms |
| Aggregation query | < 500ms | < 2000ms | < 10000ms |

### Slow Query Management

1. **Identification:** All queries are logged if they exceed 100ms (via database slow query log).
2. **Alerting:** p99 latency > threshold triggers PagerDuty alert.
3. **Analysis:** Slow queries are reviewed weekly. Each gets an EXPLAIN ANALYZE and optimization plan.
4. **Tracking:** Slow queries are tracked in a shared document with status (Identified / Optimized / Verified / Deferred).

---

## 8. Backup and Recovery Strategy

### Backup Schedule

| Environment | Type | Frequency | Retention | Storage Location |
|---|---|---|---|---|
| Development | None | N/A | N/A | N/A |
| Testing | Snapshot | Daily | 7 days | Local volume |
| Staging | Snapshot | Daily | 30 days | S3 / Blob Storage |
| Production | Continuous WAL archiving | Continuous | 7 days (WAL) | S3 / Blob Storage |
| Production | Full backup | Daily | 30 days | S3 / Blob Storage |
| Production | Weekly backup | Weekly | 90 days | S3 / Blob Storage |
| Production | Monthly backup | Monthly | 1 year | S3 / Blob Storage (Glacier) |

### Recovery Procedures

#### Point-in-Time Recovery (PITR)

1. Stop application traffic (maintenance mode).
2. Restore latest full backup to new database instance.
3. Replay WAL logs to target timestamp.
4. Validate database integrity (CHECK constraints, row counts).
5. Point application to restored database.
6. Verify data consistency with application-level checks.

#### Full Disaster Recovery

1. Provision new database instance in target region.
2. Restore latest cross-region backup.
3. Replay WAL logs to latest possible point.
4. Update DNS / connection strings to point to new instance.
5. Verify application functionality.
6. Document actual RTO and RPO for post-mortem.

### Backup Testing

- Backups are restored and validated in a test environment [WEEKLY / MONTHLY].
- A full DR drill is conducted [QUARTERLY].
- Restoration time is measured against RTO targets.

---

## 9. Data Retention Policies

| Data Category | Active Retention | Archive Retention | Deletion Policy | Legal Basis |
|---|---|---|---|---|
| User accounts | Duration of account | 90 days after deletion request | Hard delete after 90 days | GDPR right to erasure |
| Orders | 7 years | 7 years | Anonymize after 7 years | Tax/accounting regulations |
| Session data | 30 days | Not archived | Auto-delete via TTL | Security best practice |
| Audit logs | 1 year | 5 years | Hard delete after 5 years | SOC2 requirement |
| Payment info | Not stored | Not stored | Tokenized via processor | PCI-DSS requirement |
| Analytics events | 90 days | 1 year (aggregated) | Hard delete raw data | Privacy policy |

### Data Purging Process

1. Query identifies records past retention period.
2. Records are archived to cold storage (if retention policy requires).
3. Records are soft-deleted (flagged as `archived`).
4. After a grace period (30 days), records are hard-deleted in batches of 10,000.
5. Script logs counts and runs within maintenance window.
6. Failure triggers alert — no automatic retry without investigation.

---

## 10. Security Considerations

### Access Control

| Access Level | Who | What | Audit |
|---|---|---|---|
| Superuser | DBA team only | Full control | Logged |
| Read/Write | Application user | DML on all tables | Logged |
| Read-only | Read replicas | SELECT only | Logged |
| Schema migration | CI/CD user | DDL only | Logged |
| Export | Analyst user | SELECT on non-PII tables | Logged |

### Column-Level Security

| Column | Protection | Rationale |
|---|---|---|
| password_hash | Not returned in any API response, application layer exclusion | Authentication credential |
| email | Returned only to owning user and admins | PII |
| phone | Encrypted at rest (AES-256), returned only to owning user | PII |
| payment_token | Not stored in application database | PCI scope reduction |

### Encryption

- **In Transit:** All connections use TLS 1.2+ with strong cipher suites.
- **At Rest:** Database storage encryption enabled (AES-256, KMS-managed key).
- **Column Level:** Sensitive PII columns encrypted using pgcrypto (PostgreSQL) or application-level encryption.
- **Key Management:** Encryption keys are stored in AWS KMS / Azure Key Vault / HashiCorp Vault. Keys are rotated annually.

### Connection Security

- All connections require SSL/TLS.
- Database is deployed in private subnet (no public access).
- Access is granted via IAM roles / managed identities, not IP whitelisting.
- Connection credentials are rotated every 90 days.

---

## 11. Performance Considerations

### Connection Pooling

- Application uses a connection pooler with [PgBouncer / pgagroal / built-in pooler].
- Pool size is tuned for connection churn patterns:
  - `min_pool_size = max(2, concurrent_requests * 0.1)`
  - `max_pool_size = min(50, concurrent_requests * 0.5)`
- Pool timeouts prevent connection leaks.

### Query Optimization Rules

1. Always use parameterized queries (no string interpolation).
2. Avoid `SELECT *` — specify columns explicitly.
3. Use `EXISTS` over `COUNT(*)` for existence checks.
4. Use `UNION ALL` over `UNION` when duplicates are acceptable.
5. Avoid correlated subqueries — use JOIN or LATERAL instead.
6. Keep transactions short — never hold transactions across network calls.
7. Use batch inserts/updates over row-by-row operations.
8. Prefer `JOIN` over `WHERE (SELECT ...)` subqueries.

### Monitoring

| Metric | Warning Threshold | Critical Threshold | Action |
|---|---|---|---|
| Connection count | > 80% of max | > 95% of max | Scale pool / alert |
| Replication lag | > 10 seconds | > 60 seconds | Investigate / failover |
| Cache hit ratio | < 95% | < 90% | Review query patterns |
| Disk utilization | > 70% | > 85% | Add storage / archive |
| Slow queries (p99) | > 200ms | > 1000ms | Optimize / alert |
| Deadlocks | > 1 per hour | > 5 per hour | Review transaction patterns |

---

## Appendix A: Database Checklist for New Features

- [ ] New table or columns defined in migration
- [ ] Migration is backward compatible
- [ ] Indexes added for all query patterns
- [ ] Foreign keys maintain referential integrity
- [ ] Data types chosen appropriately
- [ ] Default values and constraints defined
- [ ] Migration tested with realistic data volume
- [ ] Rollback migration exists
- [ ] Data retention policy documented
- [ ] Security classification applied per column
- [ ] Performance impact assessed
- [ ] New queries profiled with EXPLAIN ANALYZE

## Appendix B: Change Log

| Date | Author | Change | Rationale |
|---|---|---|---|
| [DATE] | [AUTHOR] | Initial creation | Database baseline |
| [DATE] | [AUTHOR] | [CHANGE] | [RATIONALE] |

# SOP: Database Review
Last Updated: 2026-06-25
Owner: Database Administrator / Senior Backend Developer

## Purpose
Conduct a comprehensive review of database schema design, migration scripts, query performance, indexing strategy, data integrity mechanisms, and normalization levels. This SOP ensures the database layer is performant, maintainable, consistent, and aligned with application requirements. It produces actionable recommendations for schema optimization, query tuning, and migration safety.

## When to Execute
- When new tables or significant schema changes are proposed
- Before every production deployment that includes database changes
- When query performance issues are detected (slow queries, high CPU)
- As part of the architecture review process
- When onboarding a new service or application
- Quarterly for proactive database health assessment

## Required Inputs
- Database schema DDL scripts or migration files
- Entity Relationship Diagram (ERD) or data model documentation
- Entity Framework / ORM configuration (if applicable)
- Database migration scripts (up and down)
- Query performance data (slow query log, execution plans)
- Index usage statistics
- Data volume estimates (current and projected)
- Application query patterns (read/write ratio, hot paths)
- Database server configuration (version, hardware, settings)

## Prerequisites
- Read-only access to production or production-like database
- Database query tool (SSMS, Azure Data Studio, pgAdmin, MySQL Workbench, DBeaver)
- Query execution plan viewer (SSMS, explain plan tools)
- Index analysis queries (system DMVs, pg_stat_*, performance_schema)
- Schema comparison tool (Redgate SQL Compare, SchemaDiff, or equivalent)
- Database migration execution environment (for testing migrations)
- Test database with production-like data volume

## Procedure

### Step 1: Schema Design Review
Evaluate the overall schema design for correctness and consistency.
- **Naming conventions**:
  - Tables: plural? singular? Consistent across the schema?
  - Columns: PascalCase, snake_case, or camelCase? Consistent?
  - Primary keys: `Id`, `TableNameId`, or `PK_TableName`?
  - Foreign keys: `TableNameId` or `FK_From_To`?
  - Indexes: `IX_TableName_ColumnName` or custom pattern?
  - Check for inconsistent naming: flag any tables/columns that break the convention.
- **Data types**:
  - Are data types appropriate for the data they store?
    - INTEGER for numeric IDs (not VARCHAR)
    - DATETIME2/DATETIMEOFFSET for dates (not VARCHAR)
    - DECIMAL for money (not FLOAT)
    - NVARCHAR for Unicode text (not VARCHAR)
  - Are data types as narrow as possible? (TINYINT vs. INT, VARCHAR(50) vs. VARCHAR(MAX))
  - Flag VARCHAR(MAX)/NVARCHAR(MAX) used for small fields
  - Flag FLOAT/REAL for monetary or exact numeric values
- **Constraint review**:
  - Are primary keys defined on every table?
  - Are foreign key constraints defined where relationships exist?
  - Are CHECK constraints used for domain validation?
  - Are DEFAULT values defined for columns that need them?
  - Are NOT NULL constraints applied where appropriate?
  - Flag tables without primary keys (data integrity risk)
  - Flag missing foreign key constraints (referential integrity risk)

### Step 2: Normalization Analysis
Evaluate the schema normalization level and identify denormalization concerns.
- **Normalization level assessment**:
  - 1NF: Are all columns atomic? (no comma-separated lists, no JSON blobs for relational data)
  - 2NF: Are all non-key columns fully dependent on the primary key?
  - 3NF: Are there no transitive dependencies? (Column A → Column B → Column C)
- **Flag normalization violations**:
  - **Repeating groups**: Same-type columns (Phone1, Phone2, Phone3)
  - **Comma-separated values**: Tags in a VARCHAR column
  - **JSON columns used as relational storage** (not for flexibility, but as a workaround)
  - **Duplicate data**: Same data stored in multiple tables (synchronization risk)
- **Intentional denormalization validation**:
  - If denormalized, is there a documented reason? (performance requirement)
  - Are denormalized columns kept in sync via triggers or application logic?
  - Is the sync mechanism proven correct? (tested under concurrent access)
  - Could the performance goal be achieved with indexes or materialized views instead?
- Calculate the **normalization score**: (tables in 3NF / total tables) * 100.

### Step 3: Migration Script Review
Thoroughly review all database migration scripts for safety and correctness.
- **Migration structure**:
  - Does each migration have a unique, sequential identifier (timestamp or incremental)?
  - Does each migration have both Up() and Down() methods?
  - Are migrations independent? (can be run in any order within a version?)
  - Do migrations check preconditions before executing?
- **Migration safety checks**:
  - **Adding a column with NOT NULL**: Does it have a default value? (otherwise fails on existing rows)
  - **Removing a column**: Is there a Down script to restore it? Is the data preserved?
  - **Renaming a column/table**: Uses a multi-step process (add new → copy → drop old) not a direct rename?
  - **Changing column type**: Is the conversion safe? (INT → BIGINT is safe, VARCHAR → INT may not be)
  - **Adding a foreign key**: Is existing data validated first? (WITH NOCHECK / VALIDATE)
  - **Dropping a table**: Is there a backup strategy? Has the table been deprecated long enough?
- **Large table migrations**:
  - Does the migration batch processing for large tables (e.g., 10K rows at a time)?
  - Are there timeouts configured for long-running operations?
  - Is the migration tested against production-scale data?
  - Is there a rollback plan if the migration takes too long?
- **Data migrations**:
  - Are data transformation scripts idempotent? (rerunnable without duplicates)
  - Is there a validation step to compare before/after data?
  - Are dependent services notified of the migration completion?

### Step 4: Index Analysis
Evaluate the indexing strategy for completeness and efficiency.
- **Index inventory**:
  - List all indexes: `SELECT * FROM sys.indexes` / `\di` / `SHOW INDEXES`
  - For each index, record: table, columns (included vs. key), uniqueness, fill factor
- **Missing index detection**:
  - Run missing index DMVs:
  ```sql
  -- SQL Server
  SELECT * FROM sys.dm_db_missing_index_details
  SELECT * FROM sys.dm_db_missing_index_columns(missing_index_details.index_handle)
  
  -- PostgreSQL
  SELECT * FROM pg_stat_user_indexes
  SELECT * FROM pg_stat_all_tables WHERE seq_scan > 1000
  
  -- MySQL
  SELECT * FROM sys.schema_index_statistics WHERE rows_read > rows_changed * 10
  ```
  - Review application query patterns to find unindexed foreign keys and search columns
  - Check for composite index column order (most selective first)
  - Flag tables with no indexes beyond the primary key
- **Redundant and unused index detection**:
  - Find duplicate indexes (same column set in same order):
  ```sql
  -- SQL Server
  SELECT OBJECT_NAME(i.object_id), i.name FROM sys.indexes i
  WHERE EXISTS (
    SELECT 1 FROM sys.indexes i2 
    WHERE i2.object_id = i.object_id AND i2.index_id != i.index_id
    AND i2.key_columns = i.key_columns
  )
  ```
  - Find unused indexes:
  ```sql
  -- SQL Server
  SELECT OBJECT_NAME(s.object_id), i.name, s.* 
  FROM sys.dm_db_index_usage_stats s
  JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
  WHERE s.user_seeks + s.user_scans + s.user_lookups = 0
  
  -- PostgreSQL
  SELECT schemaname, tablename, indexname, idx_scan 
  FROM pg_stat_user_indexes WHERE idx_scan = 0
  ```
  - Flag indexes with zero usage (drop candidates)
  - Flag overlapping indexes (same leading columns)
- **Index maintenance**:
  - Check index fragmentation levels:
  ```sql
  SELECT OBJECT_NAME(ips.object_id), ips.index_id, ips.avg_fragmentation_in_percent
  FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
  WHERE ips.avg_fragmentation_in_percent > 30
  ```
  - Verify index rebuild/reorganize schedules exist
  - Check fill factor settings are appropriate for update patterns

### Step 5: Query Performance Review
Analyze query performance and identify optimization opportunities.
- **Slow query identification**:
  - Query the slow query log (or extended events/ pg_stat_statements):
  ```sql
  -- SQL Server (recent expensive queries)
  SELECT TOP 20 qs.total_elapsed_time / qs.execution_count AS avg_elapsed_time,
         qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
         SUBSTRING(st.text, (qs.statement_start_offset/2)+1, 
           ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text) 
            ELSE qs.statement_end_offset END - qs.statement_start_offset)/2) + 1) AS statement_text
  FROM sys.dm_exec_query_stats qs
  CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
  ORDER BY avg_elapsed_time DESC
  
  -- PostgreSQL
  SELECT query, calls, total_time, mean_time, rows 
  FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20
  ```
  - For each slow query, capture and analyze the execution plan
- **Common query problems**:
  - **N+1 queries**: SELECT N rows, then N additional queries:
  ```
  Select-String -Pattern "\.Include|\.ThenInclude" -Path *.cs -Recurse  # EF lazy loading
  ```
  - **Missing WHERE clauses**: full table scans on large tables
  - **Non-SARGable predicates**: `WHERE YEAR(DateColumn) = 2024` (use range query instead)
  - **Implicit conversion**: comparing VARCHAR column to INT parameter
  - **SELECT ***: retrieving all columns when only a few are needed
  - **Cursor/loop-based operations**: should use set-based operations
  - **OR conditions**: can often be replaced with UNION ALL or IN
- **Execution plan review**:
  - Identify expensive operations: table scans, key lookups, sorts, spools, hash joins
  - Check estimated vs. actual rows (large discrepancy = outdated statistics)
  - Look for warning indicators in the plan (missing join predicates, implicit conversions)
  - Verify that the most selective filters are applied earliest

### Step 6: Data Integrity Checks
Verify data integrity mechanisms are in place and correct.
- **Referential integrity**:
  - Verify foreign key constraints exist for all relationship columns
  - Check for orphaned records (WHERE NOT EXISTS scenarios)
  - Verify cascade delete/update behavior is explicitly defined (not relying on defaults)
  - Check that cascade deletes don't create unintended data loss
- **Unique constraints**:
  - Verify unique constraints/indexes on business keys (email, username, order number)
  - Check for duplicate records in columns that should be unique
  ```sql
  SELECT column, COUNT(*) FROM table GROUP BY column HAVING COUNT(*) > 1
  ```
  - Verify soft-delete tables don't have unique constraint conflicts (multiple "deleted" records)
- **Check constraints**:
  - Are CHECK constraints used for domain validation?
  - Examples: `Price > 0`, `Status IN ('Active', 'Inactive')`, `EndDate > StartDate`
  - Are constraints enforced at the database level, not just the application?
- **Trigger review** (if applicable):
  - Are triggers used for critical data validation or synchronization?
  - Are triggers auditable? (logging, version control)
  - Do triggers handle multi-row operations correctly? (not assuming single-row)
  - Flag triggers that could cause performance issues or unexpected behavior

### Step 7: ORM and Data Access Layer Review
Review how the application interacts with the database.
- **Entity Framework / ORM configuration**:
  - Are navigation properties configured correctly? (lazy loading vs. eager loading)
  - Are query projections used to limit returned columns?
  - Is AsNoTracking() used for read-only queries?
  - Are transactions configured with appropriate isolation levels?
  - Is connection pooling configured correctly?
- **Raw SQL queries**:
  - Search for raw SQL in application code:
  ```
  Select-String -Pattern "FromSqlRaw|ExecuteSqlRaw|\.SqlQuery|\.RawQuery" -Path *.cs -Recurse
  ```
  - For each raw SQL query:
    - Is it parameterized? (not string concatenation)
    - Could it be replaced with ORM query methods?
    - Is it stored in a visible location (not scattered across code)?
- **Repository pattern**:
  - Are repository methods returning IQueryable? (exposes query details to upper layers)
  - Are there methods that fetch entire tables and filter in memory?
  - Is pagination applied for queries that return multiple records?
  - Is eager loading explicitly defined (not relying on lazy loading defaults)?

### Step 8: Backup and Recovery Review
Verify backup and recovery strategies are adequate.
- **Backup configuration**:
  - Backup frequency: full (daily?), differential (hourly?), transaction log (every 5-15 min?)
  - Backup retention policy: how long are backups retained?
  - Backup storage: same region? different region? immutable?
  - Backup monitoring: alerts on backup failures?
- **Recovery testing**:
  - When was the last recovery test?
  - What is the measured RTO (Recovery Time Objective)?
  - What is the measured RPO (Recovery Point Objective)?
  - Is there a documented recovery procedure?
  - Has the recovery procedure been tested within the last quarter?
- **Point-in-time recovery**:
  - Is point-in-time recovery enabled?
  - How far back can you restore? (log backup retention period)
  - Can you restore to a specific transaction?

### Step 9: Security Review
Evaluate database security configuration.
- **Access control**:
  - List all database users and roles
  - Verify least-privilege principle (application accounts read-only where possible)
  - Check for shared accounts or accounts with no recent login
  - Verify row-level security is applied for multi-tenant data
- **Connection security**:
  - Is TLS enforced for all connections?
  - Are connection strings stored in secure vaults?
  - Is the database exposed to the internet? (should not be)
- **Audit and logging**:
  - Are schema changes logged?
  - Are sensitive data accesses logged?
  - Are failed login attempts logged and alerted?
  - Is the audit log tamper-proof?

### Step 10: Report Generation and Remediation Planning
Compile findings into a structured database review report.
- Executive summary with overall database health score (1-10).
- Categorize findings by severity:
  - **Critical** (immediate action): data loss risk, security vulnerability, migration that can't be rolled back
  - **High** (this quarter): performance degradation, missing indexes on hot paths, blocking schema issues
  - **Medium** (this year): naming conventions, missing constraints, unused indexes
  - **Low** (watch list): minor optimization, documentation gaps
- For each finding include:
  - Location (database, schema, table, migration file)
  - Description of the issue
  - Impact (data integrity, performance, maintainability, security)
  - Recommended action with code/sql example
  - Effort estimate
  - Priority ranking
- Generate index recommendations as executable SQL scripts:
  - Missing indexes to create
  - Redundant indexes to drop
  - Fragmented indexes to rebuild
- Generate query optimization recommendations as before/after examples.
- Save report as `database-review-YYYY-MM-DD.md`.

## Verification Steps
- All migration scripts are tested (Up and Down) on a production-like database
- Index recommendations are validated using query execution plans
- Referential integrity checks are run and confirm no orphan records
- Query optimization recommendations are verified to improve execution time
- Backup recovery is tested and measured against RTO/RPO targets
- Security review findings are confirmed with database access logs

## Expected Deliverables
- `database-review-YYYY-MM-DD.md` — comprehensive database review report
- Index optimization SQL scripts (create, drop, rebuild)
- Query optimization recommendations with before/after execution plans
- Migration safety review checklist
- Backup and recovery assessment report
- Security configuration review findings

## Success Criteria
- Every migration script has been reviewed for safety and reversibility
- Missing and redundant indexes are identified and documented
- Top 10 slowest queries are analyzed with optimization recommendations
- Referential integrity is verified (no orphaned records)
- Backup and recovery RTO/RPO are measured and documented
- Database health score is calculated and baseline established

## Failure Recovery
- If migration testing on production-like data is too slow: use a representative subset with documented data volume scaling assumptions
- If index usage statistics are unavailable: use query log analysis for the last 7 days
- If execution plans are too complex: focus on the top 5 most expensive operations
- If application code for raw SQL is unavailable: trace database queries using server-side tools
- If security review finds critical issues: escalate immediately, do not include in report alone
- If backup recovery test fails: document failure mode and schedule urgent remediation

## Related SOPs
- `audit.md` — Full codebase audit (includes data layer)
- `architecture-review.md` — Data architecture evaluation
- `deployment-review.md` — Migration safety in deployment context
- `performance-review.md` — Database performance in load testing
- `release-audit.md` — Database changes in release decision

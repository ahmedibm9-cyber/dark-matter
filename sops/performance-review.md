# SOP: Performance Review
Last Updated: 2026-06-25
Owner: Performance Engineer / Senior Developer

## Purpose
Systematically evaluate application performance across all layers to identify bottlenecks, measure capacity, and validate performance requirements. This SOP covers load testing, database query profiling, memory analysis, rendering performance, API latency analysis, and bundle size optimization. The output is a prioritized list of performance improvements with measured baselines and target metrics.

## When to Execute
- Before major releases or feature launches
- When performance regressions are detected in production
- When scaling to handle increased user load
- After significant architectural changes
- When user-reported slowness or timeout errors increase
- Quarterly as part of ongoing performance management
- When introducing new dependencies or third-party integrations

## Required Inputs
- Application running in a performance-testing environment
- Load testing scripts or scenarios (K6, JMeter, Artillery, locust)
- API endpoint documentation (all endpoints with expected payload sizes)
- Database server configuration and connection strings
- Production traffic patterns (peak concurrency, request mix, data volumes)
- Performance SLOs/SLAs (response time targets, throughput targets)
- Previous performance test results and baselines
- Monitoring dashboards and alert configurations

## Prerequisites
- Performance testing tools installed: K6, JMeter, Artillery, or locust
- Application Profiler: dotTrace, PerfView, MiniProfiler, or Chrome DevTools
- Database profiling: SQL Server Profiler, pg_stat_statements, or similar
- Memory analysis: dotMemory, Valgrind, heap dump analyzers
- Bundle analysis: webpack-bundle-analyzer, source-map-explorer
- Load testing environment isolated from production
- Monitoring and metrics collection (Prometheus, Grafana, Application Insights)
- Representative test data (production-like volume and distribution)

## Procedure

### Step 1: Performance Baseline Establishment
Establish current performance baselines before making changes.
- **Key baseline metrics to capture**:
  - API response times: p50, p95, p99, p99.9 (milliseconds)
  - Throughput: requests per second (RPS)
  - Error rate: percentage of failed requests
  - Database: query response times, connection pool usage, active connections
  - Memory: total memory, heap size, GC pause times, memory leak trend
  - CPU: average utilization, peak utilization
  - Network: bandwidth, latency to external services
- **Baseline test execution**:
  - Run a 15-minute warm-up with steady load
  - Then run a 30-minute load test at expected peak traffic
  - Record all metrics at 1-second granularity
  - Repeat 3 times to establish variance
- **Documentation**: Save baseline metrics as `performance-baseline-YYYY-MM-DD.json`.
- Compare against previous baselines to identify trends (improvement or regression).

### Step 2: Load Testing Scenarios
Design and execute realistic load tests.
- **Scenario design**:
  - **Happy path**: most common user journey (login → browse → action → logout)
  - **Read-heavy**: typical browse/search workload
  - **Write-heavy**: bulk operations, data imports, batch processing
  - **Peak load**: maximum expected concurrent users
  - **Stress**: 2x, 5x, 10x expected peak (find the breaking point)
  - **Endurance**: sustained load for 4+ hours (memory leak detection)
  - **Spike**: sudden 10x traffic increase in seconds (auto-scaling response)
- **Load script example (K6)**:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 100 },  // ramp up
    { duration: '30m', target: 100 }, // steady state
    { duration: '5m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function() {
  const res = http.get('https://api.example.com/endpoint');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```
- Execute each scenario and compare against baselines and SLOs.
- Record infrastructure metrics during tests (CPU, memory, network I/O, disk I/O).

### Step 3: API Latency Analysis
Profile individual API endpoints to identify slow operations.
- **Endpoint latency breakdown**:
  - Instrument each endpoint with timing:
    - Request deserialization time
    - Authentication/authorization time
    - Business logic execution time
    - External service call time (sub-calls individually)
    - Database query time (individual queries)
    - Response serialization time
  - Tools:
    - MiniProfiler (for .NET)
    - Django Debug Toolbar / Flask-Profiler (for Python)
    - express-status-monitor (for Node.js)
    - OpenTelemetry distributed tracing
- **Endpoint hotspot identification**:
  - List all endpoints sorted by p95 latency (descending)
  - List all endpoints sorted by request volume (descending)
  - Cross-reference: high-volume + high-latency = highest priority
  - Flag endpoints >500ms p95 as needing optimization
  - Flag endpoints >2s p99 as critical
- **Root cause analysis for slow endpoints**:
  - Is the database query the bottleneck? (go to Step 4)
  - Is an external API call slow? (check latency, consider caching)
  - Is serialization expensive? (large payloads, inefficient serializers)
  - Is the endpoint making N+1 database queries?
  - Is the endpoint CPU-bound (image processing, calculations)?
  - Is the endpoint I/O-bound (file uploads, data streaming)?

### Step 4: Database Query Profiling
Profile all database interactions for performance optimization.
- **Enable query logging**:
  - EF Core: `optionsBuilder.LogTo(Console.WriteLine, LogLevel.Information)`
  - SQL Server: Extended Events session for query capture
  - PostgreSQL: `pg_stat_statements` extension
  - MySQL: slow query log
- **Query analysis**:
  - For each unique query, capture:
    - Execution time (average, max, total)
    - Logical reads (pages accessed from cache)
    - Physical reads (pages read from disk)
    - Execution count (how many times is this query called?)
  - Identify the top 10 longest-running queries
  - Identify the top 10 most frequently executed queries
- **Optimization opportunities**:
  - **Missing indexes**: queries doing table scans on large tables
  - **Select N+1**: queries repeated in a loop
  ```sql
  -- Example: N+1 detection
  SELECT * FROM Orders WHERE CustomerId = @Id;  -- returns N rows
  SELECT * FROM OrderItems WHERE OrderId = @OrderId;  -- executed N times
  ```
  - **Non-SARGable WHERE clauses**: `WHERE YEAR(Date) = 2024` → `WHERE Date >= '2024-01-01' AND Date < '2025-01-01'`
  - **Implicit conversions**: comparing VARCHAR column to INT input
  - **Large result sets**: queries returning thousands of rows when only a few are needed
  - **No pagination**: queries without OFFSET/FETCH or LIMIT/OFFSET
- **Query optimization actions**:
  - For each slow query, provide the optimized version
  - Run both versions and compare execution plans
  - Document the before/after execution times

### Step 5: Memory Analysis
Analyze memory usage patterns, identify leaks, and optimize allocation.
- **Memory profiling**:
  - Run the application under load (Step 2 scenarios)
  - Capture memory snapshots at intervals (start, peak, after load, after GC)
  - Compare heap snapshots to identify growing allocations
- **Common memory issues**:
  - **Memory leaks**:
    - Event handlers not unsubscribed (subject keeps handler alive)
    - Static collections growing unbounded (caches without eviction)
    - Captured variables in closures (long-lived closures keep references)
    - Thread pool threads with ThreadLocal/AsyncLocal not cleaned up
    - Large objects in generation 2 that never get collected
  - **High allocation rate**:
    - Frequent string concatenation in loops (use StringBuilder)
    - Boxing value types repeatedly in collections
    - Temporary objects created per-request that survive to Gen 1/2
    - LINQ queries that cause repeated enumeration
  - **Memory fragmentation**:
    - Large object heap fragmentation (objects >85KB)
    - Pin handles for long periods
- **Tools**:
  - .NET: `dotnet-counters`, `dotnet-gcdump`, `dotnet-dump`
  ```
  dotnet-counters monitor --process-id <pid> System.Runtime
  dotnet-gcdump collect --process-id <pid> -o heap.dump
  ```
  - Java: `jmap`, `jhat`, Eclipse MAT
  - Node.js: `--inspect` with Chrome DevTools heap profiler
  - Python: `tracemalloc`, `memory_profiler`, `objgraph`
- **Memory optimization recommendations**:
  - Add eviction policies to caches
  - Use struct/record for small, short-lived data
  - Implement object pooling for expensive-to-create objects
  - Replace LINQ deferred execution with immediate enumeration where appropriate
  - Use ArrayPool for temporary buffers

### Step 6: Rendering and Frontend Performance
Analyze browser-side rendering performance and user experience.
- **Core Web Vitals measurement**:
  - LCP (Largest Contentful Paint): should be <2.5s
  - FID (First Input Delay): should be <100ms
  - CLS (Cumulative Layout Shift): should be <0.1
  - TTFB (Time to First Byte): should be <800ms
  - FCP (First Contentful Paint): should be <1.8s
- **Performance profiling**:
  - Chrome DevTools Performance tab: record user interaction
  - Identify long tasks (>50ms blocks main thread)
  - Check for layout thrashing (read/write cycle on DOM)
  - Check for forced reflows
  - Check for JavaScript execution time per interaction
- **Rendering issues**:
  - **Unnecessary re-renders** (React): shouldComponentUpdate/memo not used
  - **Large lists**: pagination or virtual scrolling needed
  - **Unoptimized images**: no lazy loading, no srcset, wrong formats
  - **Render-blocking resources**: CSS/JS in the head that delay rendering
  - **Excessive DOM size**: >1500 nodes or >32 levels deep
  - **Third-party scripts**: blocking rendering, excessive resource usage
- **Optimization actions**:
  - Implement code splitting (dynamic imports)
  - Optimize critical rendering path
  - Lazy load below-the-fold content
  - Use content-visibility CSS property
  - Implement service worker for caching
  - Optimize font loading

### Step 7: Bundle Size Analysis
Analyze and optimize frontend bundle sizes.
- **Bundle analysis**:
  ```bash
  # webpack-bundle-analyzer
  npx webpack-bundle-analyzer build/stats.json
  
  # source-map-explorer
  npx source-map-explorer build/static/js/*.js
  ```
- **Bundle metrics to track**:
  - Total bundle size (gzipped and uncompressed)
  - Largest modules/components
  - Duplicate modules (same library at different versions)
  - Dead code (exported but never imported)
  - Dependency weight per library
- **Optimization opportunities**:
  - **Large dependencies**: can lodash be replaced with native methods? Is moment.js necessary (vs. date-fns/luxon)?
  - **Duplicate dependencies**: same library in multiple versions from different packages
  - **Unused exports**: tree-shaking not effective due to side effects
  - **Too many polyfills**: unnecessary for modern browsers
  - **Large assets**: images, fonts, JSON data files in the bundle
- **Optimization actions**:
  - Configure proper tree-shaking
  - Implement dynamic imports for route-based code splitting
  - Replace large libraries with smaller alternatives
  - Extract CSS to separate files
  - Compress images and use modern formats (WebP, AVIF)
  - Set bundle size budgets in the build configuration:
  ```javascript
  // webpack.config.js
  performance: {
    maxAssetSize: 250000,  // 250KB
    maxEntrypointSize: 500000,  // 500KB
    hints: 'error'
  }
  ```

### Step 8: External Service Latency Analysis
Profile all external service interactions for latency and reliability.
- **Service dependency mapping**:
  - List all external service calls (APIs, databases, message queues, caches)
  - For each, record: protocol, endpoint, expected latency, timeout config
- **Latency measurement**:
  - Instrument each external call with timing:
  ```csharp
  var sw = Stopwatch.StartNew();
  var result = await externalService.CallAsync();
  sw.Stop();
  _logger.LogInformation("External call {Service} took {Elapsed}ms", 
      serviceName, sw.ElapsedMilliseconds);
  ```
  - Run under load and record p50/p95/p99 for each external dependency
- **Common issues**:
  - **Missing timeouts**: calls hang indefinitely (connection pool exhaustion)
  - **Incorrect timeout values**: too short (false failures) or too long (user waits)
  - **No retry logic**: transient failures cause errors
  - **No circuit breaker**: failing services cascade failures
  - **Chatty API**: too many small calls instead of batched requests
  - **Serialization/deserialization overhead**: large XML/JSON payloads
- **Optimization actions**:
  - Implement proper timeout policies
  - Add retry logic with exponential backoff
  - Implement circuit breaker pattern (Polly, resilience4j)
  - Batch API calls where possible
  - Consider caching responses for read-heavy external APIs
  - Move synchronous calls to async where possible

### Step 9: Concurrency and Parallelism Analysis
Evaluate thread usage, async patterns, and parallel execution.
- **Async code review**:
  - Check for sync-over-async patterns:
  ```
  Select-String -Pattern "\.Result\b|\.Wait\(\)|\.GetAwaiter\(\)\.GetResult\(\)" -Path *.cs -Recurse
  ```
  - Check for ConfigureAwait(false) consistency
  - Check for CancellationToken propagation
  - Check for async void (fire-and-forget without error handling)
- **Thread pool analysis**:
  - Monitor thread pool queue length during load tests
  - Check for thread pool starvation symptoms:
    - In-flight requests waiting for threads
    - High .NET CLR Thread Pool queue length counter
    - Slow response times across all endpoints simultaneously
- **Lock contention analysis**:
  - Profile lock contention using concurrency profiling tools
  - Check for:
    - Locks held during I/O operations
    - Fine-grained vs. coarse-grained locking choices
    - ReaderWriterLockSlim vs. lock statement appropriateness
  - Identify hot locks (contested by many threads concurrently)

### Step 10: Report Generation and Optimization Roadmap
Compile all findings into a structured performance report.
- **Executive summary**:
  - Overall performance health score (1-10)
  - SLO compliance status (are we meeting targets?)
  - Top 3 performance issues to address immediately
  - Performance trend (improving or degrading vs. last review)
- **Findings categorization**:
  - **Critical** (release-blocking): SLOs violated by >50%, service instability under load
  - **High** (sprint-blocking): SLOs at risk, >20% degradation from baseline, user-impacting slowness
  - **Medium** (backlog): optimization opportunities, <20% improvement potential, minor bottlenecks
  - **Low** (watch): nice-to-have improvements, future scalability concerns
- **For each finding**:
  - Location (endpoint, query, module, file)
  - Measured baseline and current values
  - Description of the bottleneck
  - Root cause analysis
  - Recommended fix with code/configuration example
  - Expected improvement (estimated %)
  - Effort estimate and complexity
- **Optimization roadmap**:
  - Immediate (this sprint): Critical items
  - Short-term (next 2 sprints): High items
  - Medium-term (this quarter): Medium items
  - Long-term (this year): Low items
- Save report as `performance-review-YYYY-MM-DD.md`.
- Update performance baselines with new measurements.

## Verification Steps
- All performance tests are reproducible with documented scripts
- Load test results are compared against defined SLOs with pass/fail for each
- Database query profiling identifies the top 10 slowest queries with before/after optimization plans
- Memory analysis snapshots are captured and compared
- Bundle size is measured and compared against budget
- External service latency is documented with p50/p95/p99 for each dependency

## Expected Deliverables
- `performance-review-YYYY-MM-DD.md` — comprehensive performance report
- Load test scripts and results archive
- Database query optimization recommendations with before/after execution plans
- Memory analysis report with heap dump comparisons
- Bundle analysis report with optimization opportunities
- Performance optimization roadmap with prioritized items
- Updated performance baselines

## Success Criteria
- All defined SLOs are measured and compliance is documented
- Top 10 slowest database queries are identified and optimized (with verified improvement)
- Memory leak analysis confirms no unbounded growth under 4-hour endurance test
- Bundle size is within budget (or a plan to get there)
- External service latency is documented with optimization recommendations
- Report includes effort estimates for each recommended optimization

## Failure Recovery
- If load testing environment is not representative: note the differences vs. production and adjust targets accordingly
- If database profiling impacts production: use read-replica or restore a backup to a staging server
- If external services cannot be load-tested (sandbox limitations): document the constraints and estimate based on API documentation
- If profilers cause performance degradation: use sampling profilers instead of instrumentation, or increase the sampling interval
- If test data volume is insufficient: use data generation tools (Faker, Bogus) to create production-like data distribution
- If bundle analysis exceeds time budget: focus on the top 10 largest modules first

## Related SOPs
- `database-review.md` — Detailed database performance and index analysis
- `architecture-review.md` — Architecture scalability assessment
- `audit.md` — Full codebase performance audit
- `release-audit.md` — Performance SLO verification for release
- `deployment-review.md` — Infrastructure performance configuration review

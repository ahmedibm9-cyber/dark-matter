# Known Issues

## Issue Tracking Overview

This document catalogs all currently known issues in the project. Each issue is tracked with a unique identifier, severity classification, affected version, current status, and mitigation steps. All issues are reviewed during the weekly triage meeting and updated within 24 hours of status changes.

## Severity Classification

| Severity | Definition | SLA |
|----------|------------|-----|
| **P0 - Critical** | Complete loss of core functionality, data corruption, security vulnerability | Respond within 1 hour, fix within 24 hours |
| **P1 - High** | Significant feature broken, major UI broken, performance regression >50% | Respond within 4 hours, fix within 72 hours |
| **P2 - Medium** | Feature partially broken, minor UI issues, non-critical data inconsistency | Respond within 24 hours, fix within next sprint |
| **P3 - Low** | Cosmetic issues, minor UX friction, edge cases with low impact | Respond within 1 week, fix within current quarter |
| **P4 - Trivial** | Typos, very minor styling issues, documentation gaps | Respond within 2 weeks, fix when convenient |

## Current Known Bugs

| ID | Description | Severity | Affected Version | Status | Workaround | Fix ETA |
|----|-------------|----------|-----------------|--------|------------|---------|
| BUG-001 | User session expires silently during long form fills — data lost on submission | P1 | v2.1.0 - v2.3.1 | Investigating | Save draft before submitting; use "Remember Me" to extend session | 2026-07-15 |
| BUG-002 | Date range picker off-by-one error in timezone UTC+1 or greater | P2 | v2.0.0+ | Confirmed | Manually adjust end date by +1 day | 2026-07-01 |
| BUG-003 | Export to CSV fails silently for datasets >10,000 rows | P2 | v2.2.0+ | In Progress | Use paginated export (1000 rows per request) | 2026-06-28 |
| BUG-004 | Sidebar navigation collapses when browser width is between 768px and 800px | P3 | v2.1.0+ | Triaged | Resize browser past 800px or use mobile nav toggle | 2026-08-01 |
| BUG-005 | Password reset link expires in 30 minutes but error message says 1 hour | P3 | v2.0.0+ | Open | None; request a new reset link | 2026-07-15 |
| BUG-006 | Mobile touch targets on filter dropdowns are 32px instead of required 44px | P2 | v2.3.0+ | Fix Ready | Use desktop view or zoom to 125% | 2026-06-25 |
| BUG-007 | Webhook signature validation fails when payload contains Unicode characters | P1 | v2.2.0 - v2.3.0 | Fixed (v2.3.1) | Upgrade to v2.3.1 or URL-encode payloads | Released |
| BUG-008 | Notification bell badge shows count but doesn't decrement on read | P3 | v2.3.0+ | Triaged | Refresh page to clear badge count | 2026-07-01 |
| BUG-009 | Rate limiter incorrectly resets counter on paginated API calls | P2 | v2.0.0+ | Investigating | Add 100ms delay between paginated requests | 2026-07-10 |
| BUG-010 | Multi-factor authentication backup codes not regenerating properly when refreshed | P1 | v2.3.0+ | Open | Manually note backup codes before refreshing page | 2026-06-30 |
| BUG-011 | Chart tooltip positioning breaks at right edge of viewport | P3 | v2.1.0+ | Open | Narrow browser window to center chart | 2026-08-15 |
| BUG-012 | OAuth callback URL mismatch for accounts with multiple email addresses | P2 | v2.2.0+ | Confirmed | Use primary email for OAuth sign-in | 2026-07-20 |
| BUG-013 | Search indexing fails silently when special characters (#, &, %) are in document title | P2 | v2.3.0+ | In Progress | Avoid using special characters in document titles | 2026-07-05 |
| BUG-014 | Batch operations (delete, archive) don't show progress for >50 items | P3 | v2.1.0+ | Open | Perform batch operations in groups of 50 | 2026-08-01 |
| BUG-015 | Email notifications sent twice when webhook delivery is slow (>5s) | P2 | v2.3.1+ | Investigating | Disable webhook or increase timeout threshold | 2026-07-12 |
| BUG-016 | Dark mode code blocks have poor contrast in diff view | P4 | v2.0.0+ | Open | Switch to light mode for code review | 2026-09-01 |
| BUG-017 | File upload progress stuck at 95% for files >100MB | P1 | v2.3.0+ | In Progress | Upload files smaller than 100MB individually | 2026-06-26 |
| BUG-018 | Drag-and-drop reordering resets on any filter change | P3 | v2.2.0+ | Triaged | Save custom ordering before applying filters | 2026-07-30 |
| BUG-019 | Audit log timestamps use server timezone, not user preference | P2 | v2.0.0+ | Confirmed | Cross-reference with local time when reviewing audit logs | 2026-07-08 |
| BUG-020 | API returns 500 error when optional `tags` field is null instead of omitted | P2 | v2.3.0+ | Fix Ready | Always send `tags: []` instead of `tags: null` | 2026-06-27 |

## Recurring Issues

### Session Expiration During Active Use

**Pattern**: Users with slower network connections or long-running form workflows experience silent session timeouts. The session heartbeat mechanism does not extend the TTL during active user input.

**Root Cause**: Session TTL is only refreshed on full page navigation, not on XHR requests or user interaction events.

**Related Bugs**: BUG-001

**Containment**: Implemented a session watchdog that pings the health endpoint on user interaction (mousedown, keydown, touchstart) to keep the session alive.

**Permanent Fix**: Refactor session management to use sliding expiration based on last user interaction timestamp. Scheduled for v2.4.0.

### Timezone Handling in Date Filters

**Pattern**: Users report that date range filters return results one day off when the server is in UTC and the user is in a positive UTC offset timezone.

**Root Cause**: Date comparisons are performed server-side at midnight UTC, without considering the client timezone offset. A range like "June 1 to June 5" in UTC+2 becomes "May 31 to June 4" after conversion.

**Related Bugs**: BUG-002, BUG-019

**Containment**: Added a client-side notice displaying the server timezone versus user timezone. Date picker now shows dates in user timezone with a conversion note.

**Permanent Fix**: Store all date filters as ISO 8601 date-time strings with offset, convert at query time. Scheduled for v2.4.0.

### Race Conditions in Optimistic Updates

**Pattern**: When the UI optimistically updates data and the subsequent API call fails, the rollback sometimes leaves the UI in an inconsistent state (showing a mix of old and new data).

**Root Cause**: The optimistic update cache key does not account for all query parameters, causing rollback to target the wrong cache entry.

**Related Bugs**: BUG-009, BUG-015

**Containment**: Disabled optimistic updates for mutation-heavy workflows. Users see a spinner during save operations.

**Permanent Fix**: Implement a proper cache invalidation strategy with versioned cache keys. Scheduled for v2.5.0.

## Environment-Specific Issues

### Development

| Issue | Details | Mitigation |
|-------|---------|------------|
| Hot reload causes React state loss in nested route components | Webpack HMR does not preserve state for components deeper than 3 levels | Use full page reload; avoid deep component nesting during development |
| Local SSL certificates expire monthly | mkcert certificates need regeneration every 30 days | Run `npm run certs:renew` monthly; CI reminder is set |
| Database seed script fails on PostgreSQL 15 due to deprecated USING clause | The seed SQL uses a deprecated index syntax | Upgrade to PostgreSQL 16 or apply the migration in `db/patches/postgres15-compat.sql` |
| Mock service worker (MSW) intercepts Next.js internal requests | MSW handler order conflicts with Next.js router internals | Use `bypass()` for `/__next/*` routes in MSW setup |

### Staging

| Issue | Details | Mitigation |
|-------|---------|------------|
| CDN cache takes 15 minutes to invalidate after deployment | CloudFront distribution has a minimum TTL of 15 minutes | Use query string versioning for static assets; invalidate manually via AWS console for urgent fixes |
| Email delivery delayed by 10-15 minutes | Staging Mailgun account has throttling limits | No workaround; check Mailgun logs for delivery confirmation |
| Third-party API sandbox rate limits lower than production | Stripe test mode has lower rate limits | Implement local mocks for Stripe integration during staging testing |

### Production

| Issue | Details | Mitigation |
|-------|---------|------------|
| Database connection pool exhaustion during peak hours | Max connections set to 100; peak usage reaches 95 | Connection pooling implemented via PgBouncer; monitor for additional scaling |
| Lambda cold starts cause 3-5s latency on first request after idle period | Provisioned concurrency not configured for all functions | Key API routes have provisioned concurrency; non-critical routes accept cold start latency |
| S3 upload fails for filenames with Unicode characters in IE11/Edge legacy | SDK version doesn't encode Unicode filenames | Not supported; IE11/Edge legacy are below browser support threshold (<2% traffic) |

## Third-Party Limitations

| Dependency | Limitation | Impact | Alternative |
|------------|------------|--------|-------------|
| Stripe API v2023-10 | No webhook retry differentiation between temporary and permanent failures | Webhook handler errors are all retried identically | Implement custom retry logic based on error type |
| Sentry v7.x | Breadcrumb limit of 100 per event | Long user sessions lose early breadcrumbs | Implement custom breadcrumb buffer in Sentry integration |
| PostgreSQL 14 | No native vector similarity search | Cannot implement semantic search without extension | Using pgvector extension (requires superuser during setup) |
| Redis 6 | No native support for JSON path queries | JSON data stored as strings, not native Redis JSON | Evaluate RedisJSON module or store normalized keys |
| Auth0 (free tier) | 500 MAU limit exceeded in Q2 2026 | Additional users blocked from SSO login | Upgrade to Pro tier — approved in Q3 budget |
| AWS Lambda | 15-minute execution timeout | Long-running ETL jobs exceed limit | Migrate to ECS Fargate for tasks >15 minutes |
| GraphQL (Apollo) | No built-in rate limiting | API abuse possible at query level | Implement query complexity analysis middleware |
| TinyMCE (self-hosted) | React 18 strict mode double-mount breaks initialization | Editor renders empty in dev mode | Wrap in `useEffect` with cleanup; test in production build |
| Mapbox GL JS | 50,000 map loads/month on free tier | Exceeded in Q1 2026 during beta | Evaluate MapLibre GL as open-source alternative |
| SendGrid | 100 emails/day on free tier | Staging email testing blocked after limit | Implement email sink for staging environments |

## Browser / OS Compatibility Issues

| OS | Browser | Issue | Severity | Status |
|----|---------|-------|----------|--------|
| Windows 10 | Edge 115 | CSS Grid `gap` property not applied in print mode | P3 | Workaround: Use `margin` fallback in print stylesheets |
| Windows 10 | Firefox 128 | `<dialog>` element backdrop not full-screen in fullscreen mode | P3 | Triaged — Firefox bug reported upstream |
| macOS 14 | Safari 17.5 | `aspect-ratio` CSS not respected inside flex containers | P3 | Wrap in explicit width/height container |
| macOS 14 | Chrome 126 | WebGL canvas memory leak on long-running dashboard sessions | P2 | Investigating — suspect Three.js r155 incompatibility |
| iOS 17 | Safari Mobile | Virtual keyboard pushes viewport but doesn't trigger `resize` event | P2 | Using VisualViewport API as fallback (confirmed working) |
| iOS 17 | All Browsers | File input `capture` attribute ignored on iPad | P3 | No workaround; iPadOS opens file picker instead of camera |
| Android 14 | Chrome 124 | `position: fixed` elements flicker during scroll | P3 | Applied `-webkit-overflow-scrolling: touch` as workaround |
| Android 14 | Firefox 127 | Touch events delayed by 300ms on non-`meta[name=viewport]` pages | P2 | Meta viewport tag verified on all pages |
| Linux | Firefox ESR | CSS `:has()` pseudo-class not supported | P2 | Using feature detection; provide fallback styles |
| All | All | `Intl.DateTimeFormat` returns different date formats per locale | P2 | All date displays use a centralized formatter |

## Performance Issues

| ID | Metric | Current | Target | Location | Triage |
|----|--------|---------|--------|----------|--------|
| PERF-001 | First Contentful Paint (FCP) | 2.8s | <1.5s | Dashboard page | Blocked on image optimization migration |
| PERF-002 | Largest Contentful Paint (LCP) | 4.2s | <2.5s | Document editor | Lazy loading hero image; preloading critical CSS |
| PERF-003 | Time to Interactive (TTI) | 6.1s | <3.5s | Search results page | Vendor bundle splitting needed |
| PERF-004 | Cumulative Layout Shift (CLS) | 0.25 | <0.1 | Profile settings page | Image dimensions missing on avatar, banner elements |
| PERF-005 | First Input Delay (FID) | 120ms | <100ms | Global | Third-party analytics script blocking main thread |
| PERF-006 | Lighthouse Performance Score | 62 | >90 | Homepage | Multiple render-blocking resources |
| PERF-007 | Bundle size (gzipped) | 420KB | <250KB | Main entry | Moment.js replaced with date-fns; vendor chunk optimization pending |
| PERF-008 | API response p95 latency | 1800ms | <500ms | Report generation | Database query optimization in progress |
| PERF-009 | Database query p95 | 3400ms | <200ms | Search endpoint | Full-text search index being created |
| PERF-010 | Image asset size | 5.2MB total | <1MB total | Dashboard | WebP conversion and responsive image pipeline in progress |

## Known Edge Cases Not Handled

### Data & Validation

1. **Extremely long text input** (>100KB pasted into a textarea) — UI becomes unresponsive for 2-3 seconds. No character count limiting on most textareas.
2. **Concurrent edits to same record** — The last writer wins with no merge strategy. No conflict detection or diff display.
3. **Decimal precision in currency fields** — Input accepts more than 2 decimal places but displays only 2, silently rounding without user notification.
4. **File upload with zero-byte files** — Completes successfully but produces a corrupted or empty file on download.
5. **API pagination with concurrent data changes** — If items are added/deleted during pagination, the page may show duplicates or miss records.

### UI & UX

6. **Very long dropdown options** (>50 characters) overflow the dropdown width without truncation or wrapping.
7. **Tab title doesn't reflect notification count** — The browser tab title remains static even when new notifications arrive.
8. **Empty search with wildcards** — Searching for `*` or `%` returns all results instead of showing a validation error.
9. **Network reconnect after offline** — The UI does not re-fetch data after detecting network restoration.
10. **Back button after form submission** — Submitting a form then pressing browser back shows stale data with no fresh indication.

### Mobile

11. **Landscape orientation on mobile** — Some data tables do not horizontally scroll on mobile landscape, hiding columns.
12. **Bottom sheet drag down to dismiss** — The bottom sheet component does not support gesture-based dismissal on mobile.

## How to Report New Issues

### Bug Report Template

```markdown
## Bug Report

**Title**: [Brief, descriptive title]

**Environment**:
- Version: [e.g., v2.3.1]
- Browser: [e.g., Chrome 126]
- OS: [e.g., Windows 11]
- User Role: [e.g., Admin, Editor, Viewer]

**Steps to Reproduce**:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Screenshots / Screen Recording**:
[Attach if applicable]

**Console Errors**:
[Paste any JavaScript console errors]

**Network Request**:
[Include relevant request/response if API-related]

**Impact**:
- Blocks work: Yes/No
- Affected users: [count or percentage]
- Workaround available: [description or "None"]

**Additional Context**:
[Any other relevant information]
```

### Reporting Channels

| Channel | Response Time | Best For |
|---------|--------------|----------|
| GitHub Issues | <4 hours (business hours) | All bug reports, feature requests |
| #bugs Slack Channel | <1 hour | P0/P1 issues, production incidents |
| Support Email | <8 hours | Customer-reported issues |
| In-app Feedback Widget | <24 hours | General feedback, UX issues |

## Issue Triage Process

### Daily Triage (P0/P1)

1. **Detection**: Automated monitoring alert, user report via Slack, or support ticket.
2. **Acknowledgment**: On-call engineer responds within SLA and confirms receipt.
3. **Assessment**: Determine severity, affected users, and workaround availability.
4. **Containment**: Apply mitigation (feature flag, hotfix, revert) within SLA.
5. **Resolution**: Root cause fix via normal development process.
6. **Post-mortem**: For P0 incidents, conduct a post-mortem within 5 business days.

### Weekly Triage (P2/P3)

1. **Review**: All open P2/P3 issues reviewed in weekly triage meeting (Tuesdays 10:00 AM).
2. **Reprioritize**: Severity may be escalated or downgraded based on new information.
3. **Assign**: Issues assigned to sprint or backlog with effort estimate.
4. **Update**: Status, workaround, and ETA fields updated.

### Monthly Triage (P4/Backlog)

1. **Review**: Quarterly review of all P4 and unprioritized issues.
2. **Close**: Stale issues with no activity in 6 months may be closed with a comment.
3. **Promote**: Issues that have become more relevant promoted to P3.

### Triage Decisions

| Decision | Criteria |
|----------|----------|
| **Accept** | Bug is reproducible, scope is understood, fix is feasible |
| **Reopen** | Previously closed bug re-occurred or was not properly fixed |
| **Duplicate** | Links to an existing issue, original remains open |
| **Won't Fix** | Issue is by-design, extremely low impact, or not in project scope |
| **Need More Info** | Cannot reproduce or insufficient details provided |
| **Backlog** | Valid bug but not currently prioritized |

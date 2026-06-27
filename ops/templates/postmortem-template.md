# Incident Postmortem Template

> **Purpose:** Systematically analyze incidents to prevent recurrence. Blameless, fact-driven, action-oriented.
> **Version:** 1.0.0
> **Based on:** Google SRE postmortem practices, Etsy blameless postmortem culture

---

## 1. Incident Identification

| Field | Value |
|---|---|
| **Incident ID** | `INC-{YYYY}-{NNN}` (e.g., `INC-2026-042`) |
| **Title** | Short, descriptive title |
| **Severity** | `S1` (Critical) / `S2` (High) / `S3` (Medium) / `S4` (Low) / `S5` (Minor) |
| **Status** | `investigating` / `resolved` / `mitigated` / `postmortem-draft` / `postmortem-complete` |
| **Reported By** | Name or monitoring system |
| **Postmortem Lead** | Name of postmortem facilitator |
| **Date of Incident** | YYYY-MM-DD |
| **Date of Postmortem** | YYYY-MM-DD |
| **Duration** | X hours Y minutes (detection to resolution) |
| **Tags** | `database` `performance` `security` `deployment` `dependency` `human-error` (select all that apply) |

---

## 2. Severity Definitions

| Severity | Definition | Response Time | Examples |
|---|---|---|---|
| **S1 - Critical** | Complete service outage, data loss, security breach | Immediate | All users cannot access the app, customer data exposed |
| **S2 - High** | Major feature degraded, partial outage, significant performance degradation | < 15 min | Checkout flow broken for some users, API latency > 5s |
| **S3 - Medium** | Minor feature degraded, non-critical functionality broken | < 1 hour | Profile page styling broken, non-critical report fails |
| **S4 - Low** | Cosmetic issue, minor annoyance, non-user-facing bug | < 1 week | Logging spurious error, minor UI alignment issue |
| **S5 - Minor** | Internal tool issue, no user impact | Best effort | Build warning, internal dashboard metric off |

---

## 3. Executive Summary

**One paragraph** describing the incident in plain language suitable for non-technical stakeholders.

**Example:**
On June 25, 2026, from 14:32 to 15:17 UTC, the user authentication service was unavailable due to a database connection pool exhaustion caused by a sudden traffic spike from a botnet attack. Approximately 12,500 users were unable to log in for 45 minutes. No data was lost. The root cause was an insufficient connection pool size configured for the peak traffic scenario. Mitigation involved restarting the database connection pool and rate-limiting incoming authentication requests. Long-term prevention includes dynamic connection pool sizing and DDoS protection.

---

## 4. Timeline

All times in UTC. Include timestamps for every significant event from detection to resolution.

| Time (UTC) | Event | Source |
|---|---|---|
| 14:32 | **INCIDENT BEGINS** — Botnet traffic spike begins; authentication endpoint receives 50,000 requests/min | AWS CloudWatch |
| 14:33 | Database connection pool reaches 100% utilization | Datadog alert |
| 14:34 | Authentication API response time exceeds 10s threshold | PagerDuty alert triggered |
| 14:35 | **DETECTION** — On-call engineer Jane D. paged for `AuthAPI-HighLatency` alert | PagerDuty |
| 14:36 | Jane D. acknowledges incident | PagerDuty |
| 14:37 | Jane D. investigates — checks API logs, identifies database connection errors | Log analysis |
| 14:40 | Jane D. identifies connection pool exhaustion as the symptom | Grafana dashboard |
| 14:42 | Jane D. escalates to Database Engineering (Bob K.) | Slack #incidents |
| 14:44 | Bob K. joins the call | Slack #incidents |
| 14:45 | **MITIGATION 1** — Rate limiting enabled on authentication endpoint (100 req/s per IP) | Kong config change |
| 14:47 | Rate limiting takes effect; request rate drops to 1,200 req/min | CloudWatch |
| 14:48 | Connection pool usage drops to 60% | Datadog |
| 14:49 | Authentication latency returns to < 500ms | Datadog |
| 14:51 | **INCIDENT MARKED AS MITIGATED** | PagerDuty |
| 14:55 | Bob K. starts root cause investigation | Log analysis |
| 15:05 | Root cause identified: connection pool size of 50 insufficient for 50,000 req/min | Analysis |
| 15:10 | Connection pool size increased from 50 to 200 (immediate fix) | Config change |
| 15:12 | Bob K. verifies no residual issues | Grafana |
| 15:15 | Rate limiting relaxed to 500 req/s per IP (more permissive) | Kong config change |
| 15:17 | **INCIDENT RESOLVED** — Service declared healthy; all metrics within normal range | Incident commander |
| 15:17 | **DURATION:** 45 minutes | |

**Key Metrics at Incident Peak:**
- Request rate: 50,000 req/min (normal: 500 req/min)
- Latency p95: 12.3s (normal: 200ms)
- Error rate: 73% (normal: < 0.1%)
- Affected users: 12,500
- Data loss: None

---

## 5. Detection

**How was the incident first detected?**
- [ ] Automated monitoring alert (specify system and metric)
- [ ] User report / support ticket (specify channel)
- [ ] Manual observation by engineer
- [ ] Scheduled test / health check failure
- [ ] Third-party notification (e.g., cloud provider alert)
- [ ] Other: [describe]

**Detection Delay:**
- Time from incident start to detection: X minutes
- Causes of delay (if applicable): [e.g., alert threshold too high, missing monitoring, on-call asleep]

**Monitoring Gaps Identified:**
- [ ] Missing metric: [metric name]
- [ ] Missing alert: [alert name]
- [ ] Alert threshold too high: [current vs. recommended]
- [ ] Alert fatigue causing ignore: [description]
- [ ] No dashboard: [dashboard name]

---

## 6. Root Cause Analysis — Five Whys

**Problem Statement:** The authentication service was unavailable for 45 minutes due to database connection pool exhaustion.

### Why 1: Why did the database connection pool become exhausted?
**Because** the authentication endpoint received a traffic spike of 50,000 requests/min (100x normal).

### Why 2: Why did the traffic spike occur?
**Because** a botnet launched a distributed attack against the login endpoint.

### Why 3: Why was the connection pool not sized to handle this traffic?
**Because** the connection pool was configured with a fixed size of 50, designed for normal traffic patterns (500 req/min).

### Why 4: Why was the connection pool sized for normal traffic instead of peak traffic?
**Because** the team did not consider botnet-scale traffic in the capacity planning model. Rate limiting and DDoS protection were not configured prior to the incident.

### Why 5: Why was botnet-scale traffic not considered in capacity planning?
**Because** there was no formal threat model for authentication endpoints, and no load testing was performed beyond 2x normal traffic.

### Root Cause (synthesized):
The authentication service lacked formal threat modeling and capacity planning for extreme traffic scenarios. The database connection pool was sized for normal traffic patterns without considering botnet attacks or DDoS events. No rate limiting or DDoS protection was in place on the authentication endpoint.

### Contributing Factors:
- No rate limiting on authentication endpoint
- No DDoS protection (e.g., AWS WAF, Cloudflare)
- Connection pool size was hardcoded and not dynamic
- No load testing beyond 2x normal traffic
- No formal threat model for authentication
- Missing alert on connection pool utilization above 80%

---

## 7. Impact

### User Impact
| Metric | Value |
|---|---|
| Users affected | 12,500 |
| User-facing impact | Unable to log in (authentication failure) |
| Geographic regions affected | Global |
| Duration of user impact | 45 minutes |

### Business Impact
| Metric | Value |
|---|---|
| Lost revenue (estimated) | $12,500 (based on $20/hr average revenue during peak) |
| Customer support tickets created | 47 |
| Support escalation cost | 23 hours of support staff time |
| Brand/reputation impact | Moderate — 12 tweets, 3 blog posts, 1 news article |

### Data Impact
| Metric | Value |
|---|---|
| Data loss | None |
| Data corruption | None |
| Data exposure | None |
| GDPR/regulatory breach | No |

### System Impact
| Impact | Detail |
|---|---|
| Services affected | Authentication service (100% unavailable) |
| Downstream services affected | User profile service (degraded), Session service (degraded) |
| Shared resources affected | Database primary (connection pool exhausted) |

---

## 8. Response

### Incident Response Team

| Role | Person | Actions |
|---|---|---|
| Incident Commander | Alice M. | Coordinated response, declared severity, communicated status |
| Subject Matter Expert | Jane D. | Initial triage, identified connection pool exhaustion |
| Subject Matter Expert | Bob K. | Root cause analysis, connection pool fix |
| Communications Lead | Carol S. | Status page updates, internal Slack updates, customer comms |
| Scribe | Dave R. | Timeline documentation, action item tracking |

### What Went Well
1. **Rapid detection:** Alert fired within 2 minutes of incident start
2. **Quick escalation:** Right experts were brought in within 10 minutes
3. **Effective mitigation:** Rate limiting resolved the immediate issue within 15 minutes
4. **Good communication:** Status page updated within 5 minutes of escalation
5. **Blameless culture:** Team focused on fixing the problem, not assigning blame

### What Went Wrong
1. **No rate limiting:** Authentication endpoint had no request rate limits
2. **Connection pool was static:** Not dynamically scalable
3. **Alert threshold too high:** Connection pool alert was set at 95%, not 80%
4. **No runbook:** No documented procedure for connection pool exhaustion
5. **On-call handoff delayed:** Primary on-call took 5 minutes to acknowledge (was in another meeting)

---

## 9. Resolution

### Immediate Mitigation (what stopped the bleeding)
| Action | Owner | Time | Effect |
|---|---|---|---|
| Enabled rate limiting on auth endpoint (100 req/s per IP) | Jane D. | 14:45 | Request rate dropped from 50,000 to 1,200 req/min |
| Connection pool increased from 50 to 200 | Bob K. | 15:10 | Pool utilization dropped from 100% to 40% |

### Long-Term Fix (what addresses the root cause)
| Action | Owner | Status | Timeline |
|---|---|---|---|
| Implement dynamic connection pool sizing | Bob K. | Planned | Next sprint |
| Deploy WAF with DDoS protection rules | Alice M. | In progress | This sprint |
| Create connection pool exhaustion runbook | Jane D. | Not started | Next sprint |
| Add load testing for 100x normal traffic | Dave R. | Planned | Next quarter |

### Verification of Fix
- [ ] Rate limiting test: 10,000 req/min from single IP → blocked after 100 req/s
- [ ] Connection pool test: 200 concurrent connections → pool behaves correctly
- [ ] Load test: 50,000 req/min → all requests handled within 500ms
- [ ] Monitor: Connection pool utilization alert at 80% → alert fires correctly

---

## 10. Prevention

### Systemic Fixes (prevent this class of incident)

| # | Action Item | Owner | Priority | Deadline | Status |
|---|---|---|---|---|---|
| 01 | Implement dynamic connection pool sizing (min: 10, max: 500, target: 80% utilization) | Bob K. | P1 | 2026-07-09 | Not started |
| 02 | Deploy AWS WAF with rate limiting rules for all public endpoints | Alice M. | P1 | 2026-07-02 | In progress |
| 03 | Create runbook for database connection pool exhaustion | Jane D. | P2 | 2026-07-16 | Not started |
| 04 | Run load test at 100x normal traffic for all critical endpoints | Dave R. | P2 | 2026-08-01 | Not started |
| 05 | Set connection pool utilization alert at 80% (was 95%) | Jane D. | P1 | 2026-06-26 | Completed |
| 06 | Add connection pool utilization dashboard to default view | Jane D. | P2 | 2026-07-02 | Not started |
| 07 | Conduct threat modeling workshop for all public endpoints | Alice M. | P1 | 2026-07-16 | Not started |
| 08 | Implement circuit breaker on database connection pool | Bob K. | P2 | 2026-07-23 | Not started |
| 09 | Document escalation procedure for S1/S2 incidents | Carol S. | P2 | 2026-07-09 | Not started |
| 10 | Schedule quarterly load testing exercise | Dave R. | P3 | 2026-07-16 | Not started |

### Monitoring Improvements
| Metric | Current State | Desired State | Owner | Deadline |
|---|---|---|---|---|
| Connection pool utilization | Alert at 95% | Alert at 80% | Jane D. | 2026-06-26 |
| Request rate per endpoint | Not monitored | Dashboard + alert at 5x baseline | Jane D. | 2026-07-02 |
| Rate limiting effectiveness | Not monitored | Dashboard showing blocked requests | Bob K. | 2026-07-02 |
| Database connection wait time | Not monitored | Alert at > 100ms | Bob K. | 2026-07-02 |

### Process Improvements
- Implement mandatory threat modeling for all new endpoints (owner: Alice M., deadline: 2026-08-01)
- Add capacity planning guideline to development handbook (owner: Dave R., deadline: 2026-08-01)
- Include load testing in definition of done for all P0/P1 features (owner: Alice M., deadline: 2026-07-16)

---

## 11. Action Items

### Summary of All Action Items

| # | Priority | Action Item | Owner | Deadline | Dependencies |
|---|---|---|---|---|---|
| AI-01 | P1 | Deploy WAF with DDoS protection | Alice M. | 2026-07-02 | Security team approval |
| AI-02 | P1 | Dynamic connection pool sizing | Bob K. | 2026-07-09 | (none) |
| AI-03 | P1 | Set pool utilization alert to 80% | Jane D. | 2026-06-26 | (none) |
| AI-04 | P2 | Connection pool exhaustion runbook | Jane D. | 2026-07-16 | (none) |
| AI-05 | P2 | 100x load test | Dave R. | 2026-08-01 | Load testing tool |
| AI-06 | P2 | Pool utilization dashboard | Jane D. | 2026-07-02 | (none) |
| AI-07 | P1 | Threat modeling workshop | Alice M. | 2026-07-16 | (none) |
| AI-08 | P2 | Circuit breaker on pool | Bob K. | 2026-07-23 | AI-02 |
| AI-09 | P2 | Escalation procedure doc | Carol S. | 2026-07-09 | (none) |
| AI-10 | P3 | Quarterly load testing | Dave R. | 2026-07-16 | AI-05 |

### Action Item Tracking
```
[X] AI-01 — Deploy WAF — Alice M. — 2026-07-02 — IN PROGRESS
[ ] AI-02 — Pool sizing — Bob K. — 2026-07-09 — NOT STARTED
[X] AI-03 — Alert threshold — Jane D. — 2026-06-26 — COMPLETED
[ ] AI-04 — Runbook — Jane D. — 2026-07-16 — NOT STARTED
[ ] AI-05 — Load test — Dave R. — 2026-08-01 — NOT STARTED
[ ] AI-06 — Dashboard — Jane D. — 2026-07-02 — NOT STARTED
[ ] AI-07 — Threat modeling — Alice M. — 2026-07-16 — NOT STARTED
[ ] AI-08 — Circuit breaker — Bob K. — 2026-07-23 — NOT STARTED
[ ] AI-09 — Escalation doc — Carol S. — 2026-07-09 — NOT STARTED
[ ] AI-10 — Quarterly load test — Dave R. — 2026-07-16 — NOT STARTED
```

---

## 12. Lessons Learned

### What We Learned About Our System
- Authentication endpoint is a single point of failure for multiple downstream services
- Database connection pool is the bottleneck under extreme traffic
- Rate limiting is the most effective first line of defense
- Current monitoring does not cover request rate anomalies
- Team response was effective but could be faster with better runbooks

### What We Learned About Our Process
- Threat modeling should be done before deployment, not after incidents
- Load testing at 2x normal traffic is insufficient; 100x tests reveal critical weaknesses
- Runbooks for common failure modes accelerate response time
- On-call handoff procedure needs improvement (5 min acknowledgement delay)
- Blameless postmortem culture encourages honest root cause analysis

### What We Should Continue Doing
- Automated alerting (caught incident in 2 minutes)
- Cross-team escalation (Database Engineering joined within 4 minutes)
- Incident command structure (clear roles, clear communication)
- Status page updates (kept stakeholders informed)

---

## 13. Follow-Up Review

### 30-Day Review (YYYY-MM-DD)
| Action Item | Status | Notes |
|---|---|---|
| AI-01 WAF | [ ] Not started [ ] In progress [ ] Completed | |
| AI-02 Pool sizing | [ ] Not started [ ] In progress [ ] Completed | |
| ... | | |

### 90-Day Review (YYYY-MM-DD)
| Action Item | Status | Notes |
|---|---|---|
| AI-01 WAF | [ ] Not started [ ] In progress [ ] Completed | |
| AI-02 Pool sizing | [ ] Not started [ ] In progress [ ] Completed | |
| ... | | |

### Verification of Effectiveness
- [ ] Similar incident scenario tested and handled automatically
- [ ] All action items completed and verified
- [ ] Monitoring proves new thresholds effective
- [ ] Team trained on new runbooks
- [ ] Postmortem recommendations integrated into development process

---

## 14. Approvals

| Role | Name | Date | Sign-off |
|---|---|---|---|
| Postmortem Lead | | YYYY-MM-DD | |
| Engineering Lead | | YYYY-MM-DD | |
| Product Manager | | YYYY-MM-DD | |
| Incident Commander | | YYYY-MM-DD | |
| SRE Lead | | YYYY-MM-DD | |

---

## Appendices

### A. Relevant Logs
```
[2026-06-25 14:32:15] AUTH-API: Request rate 50,000 req/min — WARNING
[2026-06-25 14:32:45] DB-POOL: Connection pool exhausted — ERROR
[2026-06-25 14:33:00] AUTH-API: Response time 10.2s — CRITICAL
[2026-06-25 14:45:00] RATE-LIMIT: Rate limiting enabled — INFO
[2026-06-25 15:10:00] DB-POOL: Pool size changed from 50 to 200 — INFO
[2026-06-25 15:17:00] AUTH-API: Service healthy — INFO
```

### B. Monitoring Dashboards
- [Link to Auth API dashboard]
- [Link to Database pool dashboard]

### C. Related Incidents
- `INC-2025-012` — Database CPU exhaustion (similar root cause pattern)
- `INC-2025-089` — API rate limiting bypass

### D. Slack / Comms Archive
- [Link to #incidents thread]
- [Link to status page updates]

### E. Changes Made During Incident
- PR #1234: Rate limiting configuration
- PR #1235: Connection pool size increase

---

> *"Every incident is a gift. It's up to us to unwrap it."*

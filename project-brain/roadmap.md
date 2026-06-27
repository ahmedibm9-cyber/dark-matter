# Product Roadmap

## Product Vision Statement

**Empower every organization to make data-driven decisions without needing a data team.** Our platform transforms complex data management into an intuitive, collaborative experience that any team member can use confidently from day one.

### Vision Pillars

1. **Zero-to-Insight in Under 5 Minutes** — New users should produce their first meaningful report within 5 minutes of signing up, with no training or documentation required.
2. **Enterprise-Grade, Consumer-Simple** — Deliver the security, compliance, and scale that enterprises require with the ease-of-use and delight that consumer products deliver.
3. **Collaborative by Default** — Data insights are a team sport. Every feature supports real-time collaboration, sharing, and discussion.
4. **Platform for Extensibility** — Our core platform provides the foundation; partners and customers extend it via APIs, webhooks, and integrations.

## Strategic Goals (Current Year: 2026)

| Goal | Metric | Current Baseline | Target | Owner |
|------|--------|-----------------|--------|-------|
| G1: Increase activation rate | % of signups who complete onboarding and perform first core action within 7 days | 42% | 65% | Product |
| G2: Reduce churn | Monthly churn rate (paid customers) | 4.8% | <2.5% | Product + Customer Success |
| G3: Enterprise adoption | Number of accounts with 50+ seats | 12 | 50 | Sales + Product |
| G4: Platform reliability | Uptime (excluding planned maintenance) | 99.5% | 99.95% | Engineering |
| G5: Customer satisfaction | NPS score | 32 | 50+ | Product + Support |
| G6: Performance | p95 API response time | 1800ms | <500ms | Engineering |
| G7: Security compliance | SOC 2 Type II certification | In progress | Certified | Security |

## Current Quarter Objectives (Q3 2026: July - September)

### Objective 1: Accelerate Time-to-Value

- **KR1.1**: Reduce onboarding completion time from 8 minutes to under 3 minutes
- **KR1.2**: Implement Quick Start template library (20 pre-built templates)
- **KR1.3**: Add in-app guided tutorials for 5 core workflows
- **KR1.4**: Achieve 60% activation rate (was 42%)

### Objective 2: Enterprise Readiness

- **KR2.1**: SOC 2 Type II certification completed
- **KR2.2**: SCIM provisioning integration (Okta, Azure AD, Google Workspace)
- **KR2.3**: Audit log export to SIEM (Splunk, Datadog)
- **KR2.4**: Custom role creation (beyond the 5 default roles)
- **KR2.5**: SAML single sign-on with Just-In-Time provisioning

### Objective 3: Platform Performance

- **KR3.1**: Reduce p95 API response time to <800ms (was 1800ms)
- **KR3.2**: Achieve 99.9% uptime (was 99.5%)
- **KR3.3**: Zero P0 incidents in Q3
- **KR3.4**: Load time for dashboard under 2 seconds on 3G

### Objective 4: AI-Powered Insights

- **KR4.1**: Natural language query interface (MVP - supports 10 query types)
- **KR4.2**: Automated anomaly detection on time-series data
- **KR4.3**: Smart Summaries - AI-generated natural language summary of any report
- **KR4.4**: Predictive trend modeling for key business metrics

## Current Sprint Goals (Sprint 18: June 22 - July 3, 2026)

### Sprint Theme: Performance and Stability

| Goal | Type | Owner | Status |
|------|------|-------|--------|
| Database query optimization: top 10 slowest queries brought under 200ms | Engineering | Alice | In Progress |
| Implement database read replicas for dashboard queries | Engineering | Bob | In Progress |
| Fix 5 P2 performance bugs (PERF-003, PERF-004, PERF-006, PERF-008, PERF-009) | Engineering | Carol | Not Started |
| Complete SOC 2 evidence collection for 10 controls | Security | Dave | In Progress |
| Migrate CircleCI to GitHub Actions for unified CI/CD | DevOps | Eve | In Progress |
| User research: 5 sessions on onboarding friction | Product | Franco | Complete |
| Design Quick Start template system | Design | Grace | In Progress |
| Build Forgot Password flow with MFA recovery | Engineering | Heidi | Not Started |

## Feature Roadmap

### Now (Q3 2026)

| Feature | Description | Status | Dependencies |
|---------|-------------|--------|-------------|
| Natural Language Query | Ask questions about data in plain English; AI generates and executes the query | Design complete, development started | GPT-4 API access, query schema mapping |
| Quick Start Templates | 20 pre-built report templates for common use cases | Design in progress | None |
| SCIM Provisioning | Automatic user provisioning/deprovisioning via SCIM 2.0 | Development in progress | Auth0 SCIM configuration |
| Custom Roles | Create custom roles with granular permission sets | Development not started | RBAC refactor (tech debt) |
| Audit Log SIEM Export | Export audit logs to Splunk, Datadog, Sumo Logic | Design in progress | Audit log schema finalized |
| Dashboard Performance | Lazy loading, query batching, edge caching | In progress | Read replicas |
| SOC 2 Type II | Complete certification audit | Evidence collection | All engineering teams |
| Onboarding Flow Redesign | Guided first-run experience with progress tracking | Design complete | Tutorial system |

### Next (Q4 2026)

| Feature | Description | Dependencies | Risk Level |
|---------|-------------|-------------|------------|
| Advanced Reporting | Custom report builder with drag-and-drop, pivot tables, calculated fields | Natural language query | Medium |
| Automated Anomaly Detection | ML-based detection of outliers in time-series data with alerting | AI pipeline infrastructure | High |
| Collaborative Annotations | Team members can annotate data points, add comments, tag colleagues | Real-time collaboration infra | Medium |
| Data Pipeline Builder | Visual ETL pipeline for importing, transforming, and scheduling data syncs | No external dependencies | High |
| Mobile App (iOS + Android) | Native mobile experience for viewing dashboards, receiving alerts | API v2 (in progress) | High |
| SAML SSO with JIT Provisioning | Enterprise SSO with Just-In-Time user creation | SCIM provisioning | Medium |

### Later (Q1 2027+)

| Feature | Description | Dependencies | Risk Level |
|---------|-------------|-------------|------------|
| API v2 (GraphQL) | Next-generation API with GraphQL, subscriptions, and granular permissions | API versioning infrastructure | High |
| White-Labeling | Custom domain, branding, and CSS for enterprise customers | Multi-tenant architecture | Medium |
| AI Report Auto-Generation | Generate full reports from natural language prompts with data sources auto-selected | Anomaly detection, NLQ | High |
| Real-Time Collaboration | Multiple users editing the same report simultaneously with presence indicators | WebSocket infrastructure | High |
| Offline Mode | View and interact with dashboards without internet connection | Mobile app, local caching | High |
| Public API Marketplace | Third-party integrations marketplace with published APIs and webhooks | API v2 | Medium |
| Advanced RBAC with Hierarchical Orgs | Nested organizations with inherited permissions and resource hierarchies | Custom roles | High |
| Data Governance Dashboard | Data lineage tracking, quality metrics, usage analytics, PII identification | Data catalog | High |
| Multi-Region Active-Active | Fully active deployment in multiple AWS regions with real-time data sync | DR setup | Very High |

## Technical Initiatives Roadmap

### Q3 2026: Foundation

| Initiative | Description | Effort | Owner |
|------------|-------------|--------|-------|
| API Performance Optimization | Query optimization, caching layer, read replicas | 6 weeks | Backend Team |
| Testing Infrastructure Improvement | Flaky test fix, CI optimization, visual regression testing | 4 weeks | QA Team |
| Dependency Upgrades | Express, Passport, Mongoose major version upgrades | 3 weeks | Backend Team |
| Logging Standardization | Centralized structured logging across all services | 2 weeks | DevOps Team |
| Design Token Implementation | Migrate hardcoded styles to design tokens | 4 weeks | Frontend Team |

### Q4 2026: Scale

| Initiative | Description | Effort | Owner |
|------------|-------------|--------|-------|
| Database Partitioning | Partition events table by date range | 3 weeks | Backend Team |
| API Versioning Strategy | Implement API versioning with v1/v2 coexistence | 4 weeks | Backend Team |
| State Management Unification | Migrate all state to single solution (Zustand) | 4 weeks | Frontend Team |
| Microservices Extraction | Extract billing service from monolith | 6 weeks | Backend Team |
| Multi-Region Deployment | Active-passive DR with automated failover | 8 weeks | DevOps Team |

### Q1 2027: Innovate

| Initiative | Description | Effort | Owner |
|------------|-------------|--------|-------|
| AI Pipeline Infrastructure | Feature store, model serving, experiment tracking | 8 weeks | ML Team |
| Real-Time Data Streaming | Kafka infrastructure for real-time event processing | 6 weeks | Backend Team |
| Mobile API Layer | GraphQL BFF for mobile clients | 4 weeks | Backend Team |
| White-Label Architecture | Tenant-specific theming and domain support | 6 weeks | Full Stack Team |

## Milestones with Dates

| Milestone | Date | Deliverable | Success Criteria |
|-----------|------|-------------|------------------|
| M1: Performance Baseline | 2026-07-15 | p95 API latency <800ms, Lighthouse score >80 | Monitored for 7 days without regression |
| M2: SOC 2 Type II | 2026-08-01 | Certification issued | No critical findings in audit report |
| M3: Quick Launch | 2026-08-15 | Onboarding flow redesign + 20 templates live | 60% activation rate within 2 weeks |
| M4: Enterprise SSO | 2026-09-01 | SAML + SCIM provisioning live | 3 enterprise customers onboarded via SSO |
| M5: AI Insights Alpha | 2026-09-15 | Natural language query + anomaly detection in alpha | Internal testing passed, 10 beta customers |
| M6: Q3 Release | 2026-09-30 | All Q3 features shipped | Release deployed, no P0/P1 bugs open |
| M7: Advanced Reporting | 2026-11-01 | Drag-and-drop report builder in beta | 50 internal users testing, feedback collected |
| M8: Mobile MVP | 2026-12-01 | iOS and Android apps in TestFlight/Play Console | Core views render, push notifications work |
| M9: Q4 Release | 2026-12-31 | All Q4 features shipped | Release deployed, Q4 OKRs reviewed |
| M10: 2026 Retrospective | 2027-01-15 | Year-end review, 2027 planning completed | Retro documented, Q1 2027 plan approved |

## Dependencies Between Initiatives

`mermaid
graph TD
    A[API Performance Optimization] --> B[Database Partitioning]
    A --> C[Read Replicas]
    B --> D[Advanced Reporting]
    C --> D
    D --> E[Mobile App]
    E --> F[GraphQL API v2]
    G[SCIM Provisioning] --> H[Custom Roles]
    H --> I[Advanced RBAC]
    J[Natural Language Query] --> K[Anomaly Detection]
    K --> L[AI Report Generation]
    M[Design Tokens] --> N[White-Labeling]
    O[Logging Standardization] --> P[SIEM Export]
    P --> Q[SOC 2 Type II]
    Q --> R[Enterprise Sales]
    S[State Management Unification] --> T[JQuery Removal]
    T --> U[React-Only Codebase]
`

### Critical Path (Q3 2026)

The critical path for Q3 is: API Performance Optimization -> Read Replicas -> SOC 2 Evidence Collection -> SOC 2 Type II. Any delay in API Performance Optimization will push all downstream milestones. Buffer: 1 week inserted between Performance Optimization and SOC 2 delivery.

## Risk Factors per Milestone

| Milestone | Risk | Probability | Impact | Mitigation |
|-----------|------|-------------|--------|------------|
| M1 (Performance) | Database partitioning takes longer than estimated due to data volume | Medium | High | Pre-partition test with production snapshot; have rollback plan |
| M2 (SOC 2) | Evidence collection incomplete due to cross-team coordination gaps | Medium | High | Weekly evidence review meetings; dedicated security team member |
| M3 (Quick Launch) | Template content not finalized due to stakeholder reviews | Low | Medium | Template skeleton shipped first; content patched in subsequent sprint |
| M4 (Enterprise SSO) | SAML metadata exchange delays with enterprise customers | Medium | Medium | Pre-build SAML metadata parser; test with 3 major IdPs internally |
| M5 (AI Insights) | LLM API cost overruns or quality issues | High | High | Implement query cost budgeting; have rule-based fallback |
| M6 (Q3 Release) | Feature scope creep | Medium | High | Feature freeze 2 weeks before release; scope buffer = 20% |
| M7 (Advanced Reporting) | Drag-and-drop library compatibility issues | Low | Medium | Evaluate 3 libraries in spike before committing |
| M8 (Mobile MVP) | Apple App Store review delays | Medium | Medium | Submit for review 2 weeks before target date |
| M9 (Q4 Release) | Holiday season reduced team availability | High | Medium | Front-load critical work in November; document handoffs |
| M10 (Retro) | Team fatigue at year end | Low | Low | Keep retro lightweight; focus on top 5 learnings only |

## Success Criteria per Milestone

| Milestone | Must Have | Should Have | Nice to Have |
|-----------|-----------|-------------|--------------|
| M1: Performance | p95 <800ms, Lighthouse >80 | No P2+ perf regressions | CI performance regression detection |
| M2: SOC 2 | Certificate issued, no critical findings | All findings addressed | Automated evidence collection |
| M3: Quick Launch | 60% activation rate, 20 templates | A/B test results | NPS improvement tracking |
| M4: Enterprise SSO | SAML + SCIM working with 3 IdPs | JIT provisioning | Directory sync status dashboard |
| M5: AI Insights | 10 query types, anomaly detection on 5 metrics | Smart Summaries on dashboards | User feedback rating system |
| M6: Q3 Release | All Q3 features shipped | <10 P2 bugs | Automated release notes |
| M7: Advanced Reporting | Drag-and-drop builder, 5 chart types | Calculated fields | Report sharing with annotations |
| M8: Mobile MVP | Dashboard view, push notifications | Report list, basic filters | Offline mode |
| M9: Q4 Release | All Q4 features shipped | OKR review automation | Year-in-review report |
| M10: Retro | Documented retro | Q1 2027 OKRs drafted | Team health survey results |

## Past Milestones and Retro Notes

### 2026 Q2 Milestones

| Milestone | Planned | Actual | Retro Note |
|-----------|---------|--------|------------|
| Q2 Performance Fixes | 2026-04-15 | 2026-04-22 | Underestimated complexity of query optimization. Need better query profiling before estimating. |
| SSO with Google Workspace | 2026-05-01 | 2026-05-01 | On time. Auth0 made this straightforward. Document configuration steps for future IdPs. |
| Report Export to PDF | 2026-05-15 | 2026-06-01 | Puppeteer rendering issues with complex dashboards. Two-week delay. Add PDF rendering to the test suite. |
| Team Dashboard v2 | 2026-06-01 | 2026-06-15 | Scope creep added 3 extra chart types mid-sprint. Use stricter scope control in future. |
| Q2 Release | 2026-06-30 | 2026-07-05 | Deployment pipeline issues caused 5-day delay. CI/CD migration to GitHub Actions is critical. |

### Q2 Retro Key Takeaways

1. **Estimation accuracy**: 60% of features estimated correctly, 30% underestimated, 10% overestimated. Actions: Add buffer for unknown unknowns; use reference class forecasting.
2. **Cross-team dependencies**: 4 features were blocked waiting on other teams. Action: Implement dependency tracking in sprint planning; create shared OKRs where dependencies exist.
3. **Technical debt impact**: 25% of Q2 engineering time spent on unplanned debt work. Action: Dedicate 20% of capacity to debt repayment starting Q3.
4. **Testing gaps**: 3 production bugs from untested edge cases. Action: Add edge case review to PR template; expand unit test coverage requirements.
5. **Communication**: Delays discovered mid-sprint, not communicated until end. Action: Implement daily standup bot asking about blockers; escalate delays >1 day immediately.

### 2026 Q1 Milestones

| Milestone | Planned | Actual | Retro Note |
|-----------|---------|--------|------------|
| User Authentication v2 | 2026-02-01 | 2026-02-15 | Auth0 migration took longer than expected due to custom JWT claims migration |
| Basic Reporting | 2026-03-01 | 2026-03-10 | Reporting engine performance issues on larger datasets |
| Q1 Release | 2026-03-31 | 2026-04-02 | Minor delay, no significant issues |

### Q1 Retro Key Takeaways

1. First quarter with new team structure had learning curve
2. Database migration tooling (Flyway) needs better pre-production validation
3. Need more investment in developer experience tooling
4. Quarterly planning process worked well, keep structure for Q2

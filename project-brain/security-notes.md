# Security Notes

## Security Architecture Overview

The application follows a defense-in-depth architecture with security controls implemented at every layer: network, infrastructure, application, and data. The architecture is designed to protect confidentiality, integrity, and availability of user data and system resources.

### Security Domains

```
┌─────────────────────────────────────────────────────────┐
│                   Authentication Layer                    │
│  (Auth0 + JWT + Session Management + MFA + SSO)          │
├─────────────────────────────────────────────────────────┤
│                   Authorization Layer                     │
│  (RBAC + ABAC + Permission Guards + API Scopes)          │
├─────────────────────────────────────────────────────────┤
│                   Application Security                    │
│  (Input Validation + Output Encoding + CSRF + XSS)       │
├─────────────────────────────────────────────────────────┤
│                   API Security                            │
│  (Rate Limiting + Request Validation + Audit Logging)    │
├─────────────────────────────────────────────────────────┤
│                   Data Security                           │
│  (Encryption at Rest + In Transit + Backup Encryption)   │
├─────────────────────────────────────────────────────────┤
│                   Infrastructure Security                 │
│  (WAF + DDoS Protection + Network Isolation + HIDS)      │
├─────────────────────────────────────────────────────────┤
│                   Compliance & Governance                 │
│  (GDPR + SOC2 + Pen Testing + Security Reviews)          │
└─────────────────────────────────────────────────────────┘
```

### Trust Boundaries

| Boundary | From | To | Protection |
|----------|------|----|------------|
| Internet → WAF | Public internet | Web application firewall | WAF rules, DDoS protection, IP filtering |
| WAF → Load Balancer | WAF | Application load balancer | Internal network, TLS termination |
| Load Balancer → App | Load balancer | Application containers | Internal network, security groups |
| App → API | Application | API servers | mTLS, API tokens, rate limiting |
| API → Database | API servers | Database cluster | Private subnet, encrypted connections, IAM auth |
| App → Cache | Application | Redis cluster | AUTH token, encrypted connections, private subnet |
| App → Storage | Application | S3/external storage | IAM roles, bucket policies, encryption at rest |

## Authentication Mechanism

### Primary Authentication (Auth0)

The application uses Auth0 as the primary identity provider with the following configuration:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Tenant | `ourcompany.us.auth0.com` | SOC2-compliant data region (US) |
| Connection | Database + Google + Microsoft | Email/password + social login + enterprise SSO |
| Token Type | RS256 JWT | Asymmetric signing; public key hosted at well-known JWKS endpoint |
| Token Expiry | Access: 15 min, Refresh: 30 days | Short-lived access tokens reduce breach window |
| Refresh Token Rotation | Enabled | Old refresh token invalidated on each refresh |
| MFA | Required for Admin, optional for others | TOTP via authenticator app or SMS backup |
| Session Management | Server-side session store (Redis) | Enables session revocation |

### JWT Structure

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "abc123def456"
}
{
  "iss": "https://ourcompany.us.auth0.com/",
  "sub": "auth0|abcdef12345678",
  "aud": ["https://api.ourcompany.com", "https://ourcompany.us.auth0.com/userinfo"],
  "iat": 1718000000,
  "exp": 1718000900,
  "scope": "openid profile email offline_access",
  "permissions": ["read:users", "write:reports", "admin:settings"],
  "org_id": "org_abc123"
}
```

### Authentication Flow

1. **Login Request**: Client redirects to Auth0 `/authorize` with PKCE code challenge.
2. **Authentication**: Auth0 authenticates user via configured connection (password, Google, Microsoft).
3. **Authorization Code**: Auth0 returns authorization code to callback URL.
4. **Token Exchange**: Server exchanges authorization code + code verifier for tokens.
5. **Token Validation**: Server validates JWT signature using Auth0 JWKS endpoint (cached, rotated weekly).
6. **Session Creation**: Server creates a session in Redis (keyed by session ID, stores user profile + permissions).
7. **Response**: Server sets HTTP-only, Secure, SameSite=Strict cookie with session ID.
8. **Subsequent Requests**: Session middleware reads cookie, fetches session from Redis, attaches user context.

### MFA Configuration

- **Required roles**: Admin, Super Admin
- **Optional roles**: Editor, Manager
- **Methods**: TOTP (preferred), SMS backup (10 codes, regenerable)
- **Remember Device**: 30 days (cookie-based, not stored)
- **Enforcement**: New device + Admin role triggers MFA challenge
- **Recovery**: 10 backup codes displayed at enrollment; admin can reset MFA via support ticket

### SSO Integration

- **Providers**: Google Workspace, Microsoft Entra ID, Okta
- **Protocol**: OIDC (preferred), SAML 2.0 (legacy)
- **Just-In-Time Provisioning**: Enabled — users created on first SSO login
- **Domain Enforcement**: Only company-managed domains allowed for SSO
- **SCIM**: Planned for Q3 2026 — automatic user provisioning/deprovisioning

## Authorization Model

### Role-Based Access Control (RBAC)

| Role | Scope | Permissions |
|------|-------|-------------|
| Viewer | Organization | Read all resources, export data |
| Editor | Organization | Create and edit resources, manage own profile |
| Manager | Organization | Editor + manage users, manage billing, view audit logs |
| Admin | Organization | Manager + manage settings, manage roles, delete resources |
| Super Admin | Global | Full access across all organizations, system configuration |

### Attribute-Based Access Control (ABAC)

ABAC supplements RBAC with fine-grained conditions:

```typescript
// Example policy: Edit document
const editDocumentPolicy = {
  effect: "Allow",
  actions: ["document:edit"],
  conditions: {
    "user.org_id === resource.org_id",      // Same organization
    "user.role IN ['Admin', 'Editor']",      // Has role
    "resource.status !== 'archived'",        // Not archived
    "resource.owner_id === user.id || user.role === 'Admin'"  // Owner or admin
  }
};
```

### Permission Guards

- **API Layer**: Express middleware (`requirePermission('users:read')`) — validates JWT permissions claim
- **Frontend**: Component guards (`can('users:create')`) — checks user store permissions
- **Database**: Row-level security policies enforce organization isolation at query level

### API Scopes

| Scope | Description | Grants |
|-------|-------------|--------|
| `openid` | Identity | Access to user's OpenID Connect claims |
| `profile` | Basic profile | Name, email, picture |
| `offline_access` | Refresh tokens | Receive refresh token for long-lived access |
| `read:users` | Read user data | GET /api/v1/users/* |
| `write:users` | Modify users | POST/PUT/DELETE /api/v1/users/* |
| `read:reports` | View reports | GET /api/v1/reports/* |
| `write:reports` | Create/modify reports | POST/PUT/DELETE /api/v1/reports/* |
| `admin:*` | Admin operations | All administrative endpoints |

## Data Classification

| Level | Definition | Examples | Handling Requirements |
|-------|------------|----------|----------------------|
| **Public** | No confidentiality requirements | Company name, product names, marketing materials | No encryption required, public distribution allowed |
| **Internal** | Not public but low sensitivity | Internal documentation, org charts, non-sensitive analytics | Encryption in transit, access based on employment |
| **Confidential** | Sensitive business data | Customer data (non-PII), revenue reports, product roadmap | Encryption at rest and transit, need-to-know access, audit logging |
| **Highly Confidential** | Legal/regulatory protected | PII, PHI, payment card data, authentication secrets | Field-level encryption, strict access controls, full audit trail, data retention policies |
| **Restricted** | Critical business secrets | Signing keys, database passwords, API tokens, encryption keys | Hardware security module (HSM), vault-based access, zero-trust model, rotation policies |

## Encryption Strategy

### At Rest

| Data Store | Encryption Method | Key Management | Status |
|------------|------------------|----------------|--------|
| PostgreSQL (primary) | AES-256-CBC, TDE | AWS KMS (automatic key rotation) | Implemented |
| PostgreSQL (backups) | AES-256-GCM | Separate KMS key, manual rotation yearly | Implemented |
| S3 (file uploads) | AES-256-S3 (SSE-S3) | AWS managed keys | Implemented |
| S3 (logs) | AES-256-KMS (SSE-KMS) | Customer-managed key, automatic rotation | Implemented |
| Redis (cache) | AES-256 (TLS + AUTH passphrase) | AUTH passphrase in Secrets Manager | Implemented |
| Elasticsearch | AES-256 at rest | KMS customer master key | Implemented |
| Backups (offsite) | GPG AES-256 + separate passphrase | Passphrase in HSM-backed vault | Implemented |

### In Transit

| Path | Protocol | Cipher | Certificate |
|------|----------|--------|-------------|
| Client → WAF | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Public CA (Let's Encrypt), 90-day rotation |
| WAF → Load Balancer | TLS 1.2+ | TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | Internal CA, auto-rotated |
| Load Balancer → App | TLS 1.2+ | Same as above | Internal CA, auto-rotated |
| App → Database | TLS 1.2+ | Same as above | RDS certificate, auto-rotated |
| App → Redis | TLS 1.2+ | Same as above | Self-signed, managed via Kubernetes secret |
| App → S3 | HTTPS | TLS 1.2+ | AWS certificate |
| Inter-service (K8s) | mTLS | Mutual TLS, SPIFFE identities | Istio Citadel, automatic rotation |

## Secrets Management

### Strategy

All secrets are stored in **AWS Secrets Manager** with automatic rotation where supported. Secrets are never committed to version control, logged, or exposed in error messages.

| Secret Category | Storage Location | Rotation | Access Pattern |
|----------------|-----------------|----------|----------------|
| Database credentials | AWS Secrets Manager | 90 days | IAM role-based access; auto-injected via Kubernetes External Secrets |
| API keys (external) | AWS Secrets Manager | 180 days | Application fetches at startup and caches in-memory |
| JWT signing keys | Auth0-managed | 30 days (automatic) | Fetched via JWKS endpoint; cached for 24 hours |
| Encryption keys | AWS KMS | Annual (automatic) | IAM policy-based access |
| TLS certificates | cert-manager (K8s) | 90 days (auto-renew) | Automatic via Let's Encrypt + cert-manager |
| Service account keys | AWS Secrets Manager | Manual | Scoped IAM roles prefered over long-lived keys |

### Prohibited Practices

- Hardcoded secrets in source code ❌
- Secrets in environment variables in deployment configs ❌
- Secrets logged to console, file, or external service ❌
- Secrets in configuration files committed to git ❌
- Sharing secrets via email, chat, or ticketing systems ❌
- Using default or weak passwords ❌

## API Security

### Authentication

- All API endpoints require authentication except: health check, public documentation, login/register, password reset
- Authentication via JWT bearer token in `Authorization` header
- JWT validated on every request (signature, expiry, issuer, audience)
- Failed authentication returns `401` with standardized error body (no details on why)

### Rate Limiting

| Endpoint Tier | Rate Limit | Burst | Applied At |
|---------------|------------|-------|------------|
| Global (per IP) | 100 req/s | 150 req/s | WAF |
| Authentication | 5 req/min per IP | 10 req/min | API Gateway + Application |
| API (authenticated) | 1000 req/min per user | 2000 req/min | API Gateway |
| Report generation | 10 req/min per user | 20 req/min | Application middleware |
| Search | 60 req/min per user | 90 req/min | Application middleware |
| Export/Download | 5 req/min per user | 10 req/min | Application middleware |

Rate limit headers returned: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
Rate limit exceeded returns `429 Too Many Requests` with `Retry-After` header.

### Input Validation

1. **Schema validation**: All request bodies validated against JSON Schema (or equivalent) before reaching business logic.
2. **Parameterized queries**: All database queries use parameterized statements or ORM. Raw SQL string concatenation is prohibited and blocked by SAST scanning.
3. **Content-Type enforcement**: API only accepts `application/json`. Returns `415` for other types.
4. **Request size limiting**: Maximum request body size: 10MB (configurable per endpoint).
5. **File upload validation**: MIME type verification, magic byte checking, file size limits (100MB max), filename sanitization.

### Output Security

- **CSP Headers**: `default-src 'self'; script-src 'self' 'strict-dynamic'; style-src 'self' 'unsafe-inline'` (allowing Tailwind-generated styles)
- **X-Content-Type-Options**: `nosniff`
- **X-Frame-Options**: `DENY`
- **Strict-Transport-Security**: `max-age=31536000; includeSubDomains`
- **Referrer-Policy**: `strict-origin-when-cross-origin`
- **Permissions-Policy**: `camera=(), microphone=(), geolocation=()`
- **Cookies**: `HttpOnly; Secure; SameSite=Strict`
- **CSRF**: Double-submit cookie pattern for non-API routes; API uses JWT + `Content-Type: application/json` enforcement

## Database Security

### Access Controls

- No direct database access from outside the VPC
- Database access restricted to application service accounts via IAM
- No hardcoded credentials — dynamic IAM tokens (RDS IAM Auth) for PostgreSQL
- Read-only replicas for reporting queries
- Row-level security (RLS) enforces organization isolation

### Audit Logging

All sensitive operations are logged to an append-only audit table:

| Action | Table | Data Logged |
|--------|-------|-------------|
| SELECT | users, payments, documents | Query pattern (not values), timestamp, user_id |
| INSERT/UPDATE/DELETE | All tables | Old values, new values, timestamp, user_id, IP |
| Login attempt | auth_log | Username, success/failure, IP, user agent |
| Permission change | roles, user_roles | Old role, new role, changed_by, timestamp |
| Data export | export_log | Exported data type, row count, user_id, timestamp |

### Query Security

- All queries use parameterized statements — no string interpolation
- ORM queries use the ORM's parameterized interface
- Stored procedures for complex operations (SELECT ... FOR UPDATE patterns)
- Query timeout: 30 seconds default, 60 seconds for reports
- Statement timeout: 30 seconds (PostgreSQL `statement_timeout`)

## Infrastructure Security

### Network Security

- **VPC**: Private subnets for all compute resources
- **Security Groups**: Least-privilege ingress/egress rules, deny by default
- **NACLs**: Stateless packet filtering at subnet level
- **WAF**: OWASP Top 10 ruleset + IP reputation lists + rate limiting
- **DDoS Protection**: AWS Shield Advanced
- **Flow Logs**: VPC flow logs sent to centralized SIEM

### Container Security (Kubernetes)

- **Image Scanning**: All images scanned by Trivy in CI; critical CVEs block deployment
- **Pod Security Standards**: Restricted policy enforced via OPA/Gatekeeper
- **Network Policies**: Deny-all default with explicit allow rules
- **Service Mesh**: Istio with mTLS for inter-service communication
- **Secrets Injection**: External Secrets Operator syncs from AWS Secrets Manager
- **Resource Limits**: CPU and memory limits on all containers (no unlimited pods)

### Monitoring and Detection

- **SIEM**: Security events sent to Splunk (Splunk Cloud)
- **Alerting**: P0 security alerts (breach, unauthorized access) routed to on-call engineer + security team
- **Anomaly Detection**: CloudTrail + GuardDuty for AWS-level anomalies
- **Endpoint Detection**: CrowdStrike Falcon on all production instances
- **Container Runtime**: Falco for container-level security monitoring

## OWASP Top 10 Compliance

| Category | Status | Mitigation |
|----------|--------|------------|
| A01: Broken Access Control | ✅ Implemented | RBAC + ABAC + permission guards tested in CI |
| A02: Cryptographic Failures | ✅ Implemented | TLS 1.3, AES-256, automated key rotation |
| A03: Injection | ✅ Implemented | Parameterized queries, input validation, SAST scanning |
| A04: Insecure Design | ⚠️ Partial | Threat modeling started; not yet integrated into sprint cycle |
| A05: Security Misconfiguration | ✅ Implemented | CIS benchmarks enforced via OPA; config validation in CI |
| A06: Vulnerable Components | ✅ Implemented | Dependency scanning (Snyk) in CI; auto-patch for critical CVEs |
| A07: Authentication Failures | ✅ Implemented | MFA required for admin; rate limiting; account lockout |
| A08: Data Integrity Failures | ⚠️ Partial | CI/CD pipeline signed; dependency verification in progress |
| A09: Security Logging Failures | ✅ Implemented | Centralized logging; audit trail for sensitive operations |
| A10: SSRF | ✅ Implemented | Network policies restrict outbound traffic; URL allowlisting |

## Security Incident Response Plan

### Incident Classification

| Class | Definition | Examples | Response Team |
|-------|------------|----------|---------------|
| **SEV-1** | Data breach, system compromise, active attack | Customer data exfiltrated, unauthorized admin access, ransomware | Full incident response team + executive notification |
| **SEV-2** | Significant security event, potential breach | Suspicious API patterns, confirmed brute force, malware detected | Security team + on-call engineer |
| **SEV-3** | Minor security event, no data exposure | Phishing attempt, port scan, policy violation | Security team during business hours |
| **SEV-4** | Informational, no action needed | Failed login attempts (normal), WAF probing | Logged for review |

### Response Steps (SEV-1)

1. **Detect**: Alert triggers (SIEM, GuardDuty, user report, automatic scan)
2. **Triage (15 min)**: On-call engineer confirms incident, determines severity, pages incident response team
3. **Contain (60 min)**: Isolate affected systems (remove from load balancer, block IPs, revoke credentials)
4. **Eradicate (4 hours)**: Remove root cause (patch vulnerability, rotate secrets, rebuild instances)
5. **Recover (2 hours)**: Restore from clean backup, verify integrity, return to production
6. **Post-Mortem (5 business days)**: Root cause analysis, timeline documentation, remediation plan

### Communication Plan

| Stakeholder | Notification Method | Timing |
|-------------|-------------------|--------|
| Incident Response Team | Phone call + Slack | Immediate |
| Engineering Lead | Slack + email | < 30 minutes |
| CTO / VP Engineering | Phone call | < 60 minutes (SEV-1 only) |
| Legal / Compliance | Email | < 4 hours (if data involved) |
| Affected Customers | Email + in-app notification | < 72 hours (regulatory) |
| Regulatory Body | Formal notification | As required by law (72h GDPR) |

## Security Review Checklist

### Pre-Release Security Review

- [ ] SAST scan passed (SonarQube, CodeQL)
- [ ] Dependency scan passed (Snyk/npm audit) — no critical/high vulnerabilities
- [ ] Secrets detection passed (no secrets in code)
- [ ] Container image scan passed (Trivy) — no critical/high CVEs
- [ ] Infrastructure scan passed (Checkov/Terraform) — no critical/high misconfigs
- [ ] API endpoints authenticated and authorized
- [ ] Input validation in place for all user-facing inputs
- [ ] Output encoding for all user-supplied data displayed in UI
- [ ] Rate limiting applied to new endpoints
- [ ] Audit logging for sensitive operations
- [ ] CSP updated if new third-party resources added
- [ ] CORS configured correctly (specific origins, not wildcard)
- [ ] Error messages do not leak sensitive information
- [ ] Database queries parameterized
- [ ] File uploads validated (type, size, content)
- [ ] Session/cookie security attributes set correctly
- [ ] New dependencies reviewed for maintenance and trustworthiness
- [ ] Feature flag toggles available for high-risk changes
- [ ] Rollback plan documented

## Penetration Testing Schedule

| Quarter | Scope | Tester | Status |
|---------|-------|--------|--------|
| Q1 2026 | Web application + API | External firm (Cure53) | Completed — 3 findings (2 low, 1 info) |
| Q2 2026 | Authentication + SSO | Internal security team | Scheduled (July 2026) |
| Q3 2026 | Full external test + infrastructure | External firm (Cure53) | Planned |
| Q4 2026 | Mobile API + internal network | Internal + external | Planned (tentative) |

## Compliance Requirements

### GDPR (General Data Protection Regulation)

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Data Processing Agreement (DPA) | ✅ In place | Signed with all sub-processors (Auth0, AWS, Stripe) |
| Data Subject Access Request (DSAR) | ✅ Implemented | Automated export in Settings > Data > Download My Data |
| Right to Erasure | ✅ Implemented | Account deletion with 30-day grace period, then hard delete |
| Data Portability | ✅ Implemented | JSON export of all user data available in Settings |
| Consent Management | ✅ Implemented | Granular cookie consent, marketing opt-in/opt-out |
| Breach Notification | ✅ Implemented | 72-hour notification workflow automated |
| Data Retention Policy | ✅ Implemented | 90-day active, 12-month archived, then deleted |
| Privacy Impact Assessment | ⚠️ In progress | Scheduled for new features involving data collection |
| DPO Appointment | ✅ Appointed | privacy@ourcompany.com |

### SOC 2 Type II

| Trust Service Criteria | Status | Evidence |
|------------------------|--------|----------|
| Security | ✅ Compliant | Access controls, monitoring, incident response tested |
| Availability | ✅ Compliant | Uptime monitoring, disaster recovery plan tested |
| Processing Integrity | ✅ Compliant | Transaction monitoring, data validation |
| Confidentiality | ✅ Compliant | Encryption, access controls, NDAs |
| Privacy | ✅ Compliant | GDPR alignment, privacy notice, data handling policies |

### Additional Compliance

| Standard | Applicable? | Status |
|----------|------------|--------|
| PCI DSS | No (Stripe handles payment processing) | N/A — Stripe is PCI-compliant Level 1 |
| HIPAA | Not applicable (no PHI processed) | N/A |
| ISO 27001 | Planned for 2027 | Gap assessment scheduled Q4 2026 |
| CCPA | Applicable to California users | Implemented — opt-out mechanism in Settings |

## Security Contact Information

| Role | Name | Email | Phone (Emergency) |
|------|------|-------|-------------------|
| Security Lead | Jane Smith | jane.smith@ourcompany.com | +1-555-0101 |
| CISO | Robert Chen | robert.chen@ourcompany.com | +1-555-0102 |
| DPO | Maria Garcia | maria.garcia@ourcompany.com | +1-555-0103 |
| Incident Response | security@ourcompany.com | security@ourcompany.com | +1-555-0199 |
| Vulnerability Disclosure | security@ourcompany.com | security@ourcompany.com | PGP key: https://ourcompany.com/security.txt |

### Vulnerability Disclosure Program

We maintain a responsible disclosure program. Security researchers are invited to report vulnerabilities via security@ourcompany.com. We commit to:
- Acknowledging receipt within 24 hours
- Providing status updates every 5 business days
- Fixing critical/high vulnerabilities within 30 days
- Medium/low vulnerabilities within 90 days
- Public disclosure coordinated with reporter
- Bug bounty rewards available for qualifying reports (see `SECURITY.md` in repository root)

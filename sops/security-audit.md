# SOP: Security Audit
Last Updated: 2026-06-25
Owner: Security Lead / CISO

## Purpose
Perform a comprehensive security assessment of the application to identify vulnerabilities, configuration weaknesses, and security control gaps. This SOP covers automated scanning, manual code review for security patterns, dependency vulnerability analysis, and infrastructure security review. The output is a prioritized remediation plan aligned with OWASP Top 10 and industry best practices.

## When to Execute
- Before every production release (mandatory for major releases)
- When integrating third-party components or APIs
- After discovering a security incident
- Quarterly for all active projects
- When PCI-DSS, HIPAA, SOC2, or other compliance requirements apply
- Onboarding new applications into the security program

## Required Inputs
- Repository access with all source code
- Infrastructure configuration (Terraform, CloudFormation, Helm charts, Docker files)
- Dependency manifest files (package.json, packages.config, *.csproj, requirements.txt, etc.)
- Authentication and authorization architecture documentation
- Network topology and firewall rules
- Previous security audit reports and penetration test results
- Compliance requirements checklist

## Prerequisites
- OWASP ZAP or Burp Suite Community/Pro installed
- npm audit, dotnet list package --vulnerable, pip audit, or trivy installed
- Secrets scanning tool (truffleHog, Gitleaks, or GitHub secret scanning)
- Static analysis security tool (Semgrep, CodeQL, or SonarQube)
- Dependency vulnerability database access (Snyk, GitHub Advisory DB, NVD)
- Docker and container scanning tools (Trivy, Clair)
- Network scanning tools (Nmap, masscan) if infrastructure is in scope

## Procedure

### Step 1: Automated Vulnerability Scanning
Run comprehensive automated scans across all layers.
- SAST (Static Application Security Testing):
```
# Semgrep
semgrep --config=auto --output=sast-results.json --json
# CodeQL
codeql database create codeql-db --language=<language>
codeql database analyze codeql-db --format=sarif-latest --output=codeql-results.sarif
```
- DAST (Dynamic Application Security Testing) against staging environment:
```
# OWASP ZAP
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' https://staging-app.example.com
```
- Container scanning:
```
trivy image --severity CRITICAL,HIGH --format json --output trivy-results.json <image-name>
```
- Infrastructure scanning:
```
tfsec terraform/  # Terraform security scanning
checkov --directory .  # Infrastructure as Code scanning
```

### Step 2: OWASP Top 10 Verification
Systematically verify each OWASP Top 10 category.
- **A01: Broken Access Control**
  - Search for missing authorization attributes:
  ```
  Select-String -Pattern "\[AllowAnonymous\]|\[Authorize\]" -Path *.cs -Recurse
  ```
  - Check that `[Authorize]` is on controllers/endpoints, not just on individual actions.
  - Verify role-based access control is enforced server-side.
  - Look for IDOR patterns: `Select-String -Pattern "\.\.\/\.\.\/|user\.Id\s*==\s*request\.Id" -Path *.cs -Recurse`
- **A02: Cryptographic Failures**
  - Check for weak algorithms: `Select-String -Pattern "MD5|SHA1|DES|3DES|RC2|RC4" -Path *.cs -Recurse`
  - Verify TLS enforcement: `Select-String -Pattern "http://" -Path *.cs -Recurse | Where-Object { $_ -notmatch "localhost" }`
  - Check for hardcoded certificates or keys.
- **A03: Injection**
  - SQL injection: `Select-String -Pattern "\.RawQuery|\.ExecuteSqlRaw|\.FromSqlRaw" -Path *.cs -Recurse`
  - Command injection: `Select-String -Pattern "Process\.Start|ShellExecute|\.cmd" -Path *.cs -Recurse`
  - NoSQL injection: Check for unsanitized MongoDB/Lucene queries.
  - LDAP injection: Check for unsanitized LDAP filter strings.
- **A04: Insecure Design**
  - Review architecture for missing rate limiting, missing audit logs, trust boundaries.
  - Check for missing CSRF tokens on state-changing endpoints.
  - Verify that security is enforced by default, not opt-in.
- **A05: Security Misconfiguration**
  - Check for debug/developer endpoints in production configuration.
  - Verify CORS configuration is restrictive: `Select-String -Pattern "AllowAllOrigins|\*" -Path Startup.cs, Program.cs -Recurse`
  - Check that default credentials are changed.
  - Verify security headers: `curl -s -D- https://staging-app.example.com | Select-String -Pattern "Strict-Transport-Security|X-Content-Type-Options|X-Frame-Options|Content-Security-Policy"`
- **A06: Vulnerable and Outdated Components**
  - Cross-reference dependency versions with CVE databases.
  - Check for components >2 versions behind latest stable.
  - Identify EOL runtimes and frameworks.
- **A07: Identification and Authentication Failures**
  - Verify password policies (length, complexity, lockout) are enforced server-side.
  - Check for session management vulnerabilities (fixed session IDs, no session timeout).
  - Verify MFA implementation if applicable.
  - Check for weak JWT secrets: `Select-String -Pattern "secret.*=.*[""'][a-zA-Z0-9]{1,16}[""']" -Path *.json, *.cs -Recurse`
- **A08: Software and Data Integrity Failures**
  - Verify CI/CD pipeline security (no unsigned commits, protected branches).
  - Check for subresource integrity on CDN-loaded scripts.
  - Review dependency sources (are they pulling from official registries?).
- **A09: Security Logging and Monitoring Failures**
  - Verify that security-relevant events are logged: login attempts, privilege changes, data exports.
  - Check that logs include: timestamp, user ID, source IP, action, resource, result.
  - Verify logs cannot be tampered with (immutable storage, append-only).
- **A10: Server-Side Request Forgery (SSRF)**
  - Check for user-controlled URLs fetched server-side:
  ```
  Select-String -Pattern "HttpClient.*Get|WebClient.*Download|RestClient.*Execute" -Path *.cs -Recurse
  ```
  - Verify URL validation and allowlisting.

### Step 3: Secrets Scanning
Search the entire codebase and git history for exposed secrets.
```
# TruffleHog
trufflehog git file://. --results=verified --json > secrets-report.json
# Gitleaks
gitleaks detect --source . --report-path gitleaks-report.json --verbose
```
- Check for:
  - API keys, tokens, and passwords in source code
  - Connection strings with embedded credentials
  - Private keys (.pem, .key, .p12 files)
  - .env files committed to version control
  - Hardcoded certificates
- For each finding: verify if the secret is still active, determine exposure window, initiate rotation.
- Search git history: `git log -p --diff-filter=M --name-only | Select-String -Pattern "password|secret|api_key|token"`

### Step 4: Authentication and Authorization Deep Dive
Perform a manual review of the auth system.
- **Authentication flow review:**
  - Trace the complete login flow: credentials → hashing/encryption → storage → verification → session token.
  - Verify password hashing uses bcrypt, argon2, or PBKDF2 (not MD5, SHA1, or unsalted SHA256).
  - Check for timing-safe comparison on password/OTP verification.
  - Verify account lockout after N failed attempts (typically 5-10).
  - Check for "remember me" token security (signed, rotated on use).
- **Authorization flow review:**
  - Trace a request from controller → service → data access.
  - Verify authorization checks at each layer, not just the API gateway.
  - Check for horizontal privilege escalation (User A accessing User B's data).
  - Verify admin endpoints require elevated roles, not just hidden URLs.
- **Token/JWT review:**
  - Check signing algorithm (RS256 or ES256 preferred, reject `none` algorithm).
  - Verify expiration is set and short-lived (<15 minutes for access tokens).
  - Check that JWTs are validated (signature, expiry, issuer, audience).
  - Verify tokens are not logged or stored in URLs.

### Step 5: Input Validation and Output Encoding Review
Verify all user inputs are validated and outputs are encoded.
- Check for:
  - Missing input validation on all controller action parameters
  - Weak validation that only checks client-side
  - Missing allowlist validation (prefer allowlists over blocklists)
  - Missing output encoding in views/templates
  - XSS patterns in frontend code:
  ```
  Select-String -Pattern "innerHTML|outerHTML|dangerouslySetInnerHTML|v-html" -Path *.js, *.ts, *.vue, *.jsx -Recurse
  ```
  - Unsafe URL handling: `Select-String -Pattern "window\.location|document\.location|\.href\s*=" -Path *.js, *.ts -Recurse`
- Verify file upload validation:
  - File type validation (magic bytes, not just extension)
  - File size limits
  - Virus scanning on upload
  - Storage outside webroot with random filenames

### Step 6: API Security Review
Audit all API endpoints for security best practices.
- Enumerate all API routes:
  - If .NET: `Select-String -Pattern "\[HttpGet|\[HttpPost|\[HttpPut|\[HttpDelete|\[Route" -Path *.cs -Recurse`
  - If Node: review route definitions in express/fastify files.
- For each endpoint verify:
  - Authentication required (except explicitly public)
  - Authorization matches the principle of least privilege
  - Rate limiting is applied
  - Request size limits are configured
  - Response doesn't leak internal information (stack traces, server versions)
  - Appropriate HTTP status codes (no 500 on validation errors, no 200 on auth failures)
- Check GraphQL endpoints specifically:
  - Query depth and complexity limiting
  - Batch request rate limiting
  - Introspection disabled in production

### Step 7: Infrastructure Security Review
Review deployment and infrastructure configuration.
- **Network security:**
  - Verify least-privilege firewall rules
  - Check that databases are not publicly accessible
  - Verify TLS termination is secure (TLS 1.2+)
- **Container/Orchestration security:**
  - Check Docker images are not running as root
  - Verify resource limits are set on containers
  - Check Kubernetes RBAC is configured
  - Verify secrets are mounted from secret stores, not env variables
- **Cloud security:**
  - Review IAM roles for least privilege
  - Check S3/blob storage for public access
  - Verify CloudTrail/Audit Logging is enabled
  - Check for unused security groups/resources

### Step 8: Compliance Verification
If applicable, verify compliance with relevant standards.
- **PCI-DSS**: encryption of cardholder data, access control, logging, quarterly scans
- **HIPAA**: BAA verification, audit controls, integrity controls, transmission security
- **SOC2**: security monitoring, change management, risk mitigation
- **GDPR**: data minimization, consent mechanisms, data deletion capability, breach notification
- For each requirement, document evidence of compliance or gap analysis.

### Step 9: Report Generation and Remediation Planning
Compile all findings into a structured security report.
- Executive summary with risk score (Critical/High/Medium/Low).
- For each finding:
  - Title and description
  - CVSS score (if applicable)
  - Affected component and file location
  - Reproduction steps or evidence
  - Business impact
  - Recommended fix with code example
  - Effort estimate (hours)
- Generate a remediation roadmap:
  - Immediate (0-7 days): Critical vulnerabilities, active exploits, exposed secrets
  - Short-term (1-4 weeks): High severity, compliance gaps
  - Medium-term (1-3 months): Medium severity, hardening improvements
  - Long-term (3-12 months): Low severity, defense in depth
- Save as `security-audit-YYYY-MM-DD.md`.

### Step 10: Follow-up Verification
After remediation, verify fixes are effective.
- Re-run automated scanners on fixed code.
- Perform manual verification of each Critical/High fix.
- Test that fixes don't introduce regressions (run the test suite).
- Update the threat model with new findings and mitigations.
- Schedule the next audit cycle.

## Verification Steps
- All automated scans completed without errors and results documented
- OWASP Top 10 verification checklist is fully populated (pass/fail/NA per item)
- Secrets scan covers both current files and full git history
- No confirmed secrets remain active after remediation
- Authentication and authorization flows have been traced end-to-end
- Infrastructure configuration passes automated policy checks

## Expected Deliverables
- `security-audit-YYYY-MM-DD.md` — full security audit report
- `sast-results.json` / `codeql-results.sarif` — raw SAST findings
- `secrets-report.json` — secrets scan results with remediation status
- Remediation backlog in project tracking system with severity labels
- Updated threat model document (if it exists)
- Compliance gap analysis (if applicable)

## Success Criteria
- All Critical and High vulnerabilities identified have verified remediations
- No secrets in git history remain unrotated
- OWASP Top 10 verification shows zero Critical failures
- SAST scan achieves <5% false positive rate on High+ findings
- All discovered vulnerabilities are reproducible and documented
- Remediation plan includes timeline and owner for every finding

## Failure Recovery
- If SAST tool produces too many false positives: create a `.semgrepignore` / `.codeqlignore` and tag known false positives, then re-run
- If DAST scan crashes the staging environment: coordinate with DevOps, use rate-limited scanning, schedule during low traffic
- If secrets scan on full git history exceeds time budget: use `--since` flag to limit to last 12 months, note coverage gap
- If dependencies exceed vulnerability scan limits: use tiered approach — scan direct deps first, then top-level transitive deps
- If penetration testing is scoped but resources unavailable: document the gap and schedule for next quarter

## Related SOPs
- `audit.md` — Full codebase audit (includes security overview)
- `dependency-review.md` — Detailed dependency vulnerability analysis
- `code-review.md` — Security-focused code review practices
- `deployment-review.md` — Infrastructure security configuration review
- `release-audit.md` — Go/no-go decision including security criteria

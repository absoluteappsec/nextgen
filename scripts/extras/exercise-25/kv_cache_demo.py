"""
Exercise 25: KV Cache Reuse Demo (Latent Briefing Concept)

Demonstrates how Anthropic's prompt caching reuses KV cache representations
across multiple queries — the same core mechanism described in Ramp's
"Latent Briefing" paper (https://labs.ramp.com/research/latent-briefing-kv-cache).

The large security policy is cached on the first call. Subsequent calls reuse
the cached KV representations, avoiding redundant computation.
"""

import os
from dotenv import load_dotenv
from anthropic import AnthropicBedrock

load_dotenv()

client = AnthropicBedrock(
    aws_region=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
)

MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

SECURITY_POLICY = """\
ACME CORPORATION — APPLICATION SECURITY POLICY v4.2

1. AUTHENTICATION & ACCESS CONTROL
All services must implement multi-factor authentication (MFA) for user-facing
endpoints. API-to-API communication must use short-lived tokens (maximum 15-minute
lifetime) issued by the central identity provider. Service accounts must never use
static credentials. OAuth 2.0 with PKCE is the required flow for all browser-based
clients. Session tokens must be rotated after privilege escalation events (e.g.,
entering an admin panel). Failed authentication attempts must trigger progressive
delays: 1s after 3 failures, 5s after 5, and account lockout after 10.

2. SECRETS & CREDENTIAL MANAGEMENT
All secrets must be stored in HashiCorp Vault or AWS Secrets Manager. Hardcoded
credentials in source code are a P0 finding and must be remediated within 24 hours.
Database credentials must be rotated every 30 days via automated rotation policies.
API keys issued to external partners must have per-endpoint scoping and rate limits.
TLS certificates must use 2048-bit RSA or P-256 ECDSA minimum and auto-renew 30 days
before expiry. SSH keys must use Ed25519; RSA keys below 4096 bits are prohibited.

3. DATA CLASSIFICATION & HANDLING
Data is classified into four tiers: Public, Internal, Confidential, and Restricted.
PII (names, emails, SSNs, payment info) is always Restricted. Restricted data must be
encrypted at rest with AES-256-GCM and in transit with TLS 1.3. Internal data may use
TLS 1.2 minimum. Logs must never contain Restricted data — structured logging with
redaction filters is required. Data retention: Restricted=1 year, Confidential=3 years,
Internal=5 years, Public=indefinite. Cross-border transfers of Restricted data require
legal review and must comply with GDPR, CCPA, and relevant local regulations.

4. SECURE DEVELOPMENT LIFECYCLE
All code must pass SAST scanning (Semgrep + CodeQL) before merge. DAST scanning runs
nightly against staging environments. Dependency scanning (SCA) blocks PRs that
introduce critical/high CVEs with known exploits. Container images must be rebuilt
weekly to pick up base image patches. Developers must complete secure coding training
annually — OWASP Top 10, injection prevention, and authentication design. Threat
modeling is required for all new features handling Restricted data or modifying
authentication flows.

5. INCIDENT RESPONSE PROCEDURES
Security incidents are classified P0-P3. P0 (active breach or data exfiltration):
15-minute initial response, all-hands war room, executive notification within 1 hour.
P1 (confirmed vulnerability being exploited): 1-hour response, designated responder
team. P2 (vulnerability identified, not exploited): 24-hour triage, patch within 7
days. P3 (informational/hardening): tracked in backlog, addressed within 30 days. All
incidents require a post-mortem within 5 business days. Root cause analysis must
identify systemic fixes, not just immediate patches. Communication to affected users
must occur within 72 hours for any P0/P1 involving PII.

6. NETWORK SEGMENTATION & INFRASTRUCTURE
Production, staging, and development environments must be fully isolated — no shared
databases, no shared credentials, no network paths between them. Internal services
communicate via mTLS within a service mesh. Public-facing endpoints must sit behind a
WAF with OWASP CRS ruleset enabled. Egress traffic must be explicitly allowlisted —
default-deny. Database access from application tiers must go through a connection
pooler with query parameterization enforced at the driver level.

7. LOGGING, MONITORING & ALERTING
All authentication events, authorization failures, and data access to Restricted
resources must be logged with structured fields: timestamp, actor, action, resource,
outcome, source IP. Logs must be shipped to the SIEM within 60 seconds. Alerting rules:
>5 failed auth attempts from a single IP in 60s triggers investigation, any access to
Restricted data outside business hours triggers P2 review, any disabled WAF rule
triggers immediate P1. Log retention: 90 days hot, 1 year cold, 7 years archive for
compliance. Tampering with audit logs is a terminable offense.

8. THIRD-PARTY & SUPPLY CHAIN SECURITY
All third-party libraries must be pinned to exact versions with integrity hashes.
Transitive dependency updates require automated testing before promotion. Vendors with
access to Restricted data must complete SOC 2 Type II review annually. Open-source
components must have active maintenance (commit within 6 months) or an approved
exception. Container base images must come from the approved registry — no pulling
directly from Docker Hub in production builds.

9. API SECURITY STANDARDS
All APIs must implement rate limiting: 100 requests/minute for authenticated users, 20
requests/minute for unauthenticated endpoints. GraphQL endpoints must enforce query
depth limits (max 10) and complexity scoring (max 1000 points). REST APIs must validate
Content-Type headers and reject unexpected media types. All API responses must include
security headers: X-Content-Type-Options: nosniff, X-Frame-Options: DENY,
Strict-Transport-Security with max-age of at least 31536000. CORS policies must
explicitly whitelist allowed origins — wildcard (*) is prohibited for any endpoint
handling authenticated requests. API versioning is mandatory; deprecated versions must
log warnings for 90 days before removal. Input validation must occur at the API gateway
layer using JSON Schema validation with strict mode enabled. File upload endpoints must
validate MIME types server-side, enforce size limits (50MB default), and scan with
ClamAV before storage. WebSocket connections must authenticate on handshake and
re-validate tokens every 15 minutes.

10. MOBILE & CLIENT-SIDE SECURITY
Mobile applications must implement certificate pinning with backup pins. Local storage
of Restricted data requires hardware-backed encryption (Keychain/Keystore). Binary
obfuscation is required for release builds. Debug builds must never be distributed
outside the development team. Client-side validation must always be duplicated
server-side — client validation is for UX only, never for security. JavaScript
applications must implement Subresource Integrity (SRI) for all third-party scripts.
Content Security Policy must be enforced in report-and-enforce mode with nonce-based
script allowlisting. Local storage and session storage must never contain tokens or PII.
"""

system_blocks = [
    {
        "type": "text",
        "text": "You are an application security engineer. Answer questions using the security policy below.",
    },
    {
        "type": "text",
        "text": SECURITY_POLICY,
        "cache_control": {"type": "ephemeral"},
    },
]

queries = [
    "What are the authentication requirements for API-to-API communication and browser clients?",
    "Describe the credential rotation and secrets management requirements.",
    "What are the incident response SLAs for a P0 vs P1 security incident?",
]

print("=" * 60)
print("Exercise 25: KV Cache Reuse Demo (Latent Briefing Concept)")
print("=" * 60)
print()
print(f"Security policy size: ~{len(SECURITY_POLICY.split())} words")
print(f"Sending {len(queries)} queries against the same cached context...")
print()

for i, query in enumerate(queries, 1):
    print(f"--- Query {i} ---")
    print(f"Q: {query}")
    print()

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=system_blocks,
        messages=[{"role": "user", "content": query}],
    )

    print(f"A: {response.content[0].text[:300]}")
    print()

    usage = response.usage
    cache_created = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0

    print(f"  Input tokens:          {usage.input_tokens}")
    print(f"  Output tokens:         {usage.output_tokens}")
    print(f"  Cache creation tokens: {cache_created}")
    print(f"  Cache read tokens:     {cache_read}")

    if cache_created > 0:
        print("  --> KV cache CREATED (one-time cost)")
    if cache_read > 0:
        print("  --> KV cache READ (reuse! no recomputation)")
    print()

print("=" * 60)
print("TAKEAWAY: When prompt caching is active, calls 2 and 3 show")
print("cache_read tokens instead of cache_creation tokens. The model")
print("reuses pre-computed KV representations — the same mechanism")
print("Ramp's Latent Briefing paper uses to share context between")
print("orchestrator and workers.")
print()
print("If cache metrics show 0, prompt caching may not be enabled")
print("for this model/region. The cache_control block is still")
print("correctly structured — metrics will populate when supported.")
print("=" * 60)

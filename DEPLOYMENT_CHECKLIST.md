# NovaBot Deployment Checklist

## Secrets & Environment
- [ ] DJANGO_SECRET_KEY rotated & stored in hosting env vars.
- [ ] ALLOWED_HOSTS set to production domains.
- [ ] CORS_ALLOWED_ORIGINS lists exact frontend origins (https://app.example.com).
- [ ] Mongo credentials least-privilege (readWrite on target DB only).
- [ ] OPENAI_API_KEY / GEMINI_API_KEY present (or features disabled gracefully).
- [ ] FIREBASE_PROJECT_ID + FIREBASE_CREDENTIALS_JSON (base64 or inline JSON) configured if Firebase auth used.
- [ ] SECURE_SSL_REDIRECT=true (behind HTTPS) & HSTS active.

## Build & Static Assets
- [ ] collectstatic runs without errors.
- [ ] Whitenoise serves /static/ assets (check a CSS file returns 200).

## Database & Data Stores
- [ ] Django migrations applied.
- [ ] Mongo cluster accessible from hosting provider (IP allowlist or VPC peering).
- [ ] Backups / snapshots strategy documented.

## API Surface
- [ ] / returns root JSON with version.
- [ ] /api/health/ returns status ok or degraded (investigate degraded before go-live).
- [ ] Versioned alias /api/v1/ functional (prepare clients to move there later).

## Observability
- [ ] Sentry or alternative monitoring DSN configured (optional but recommended).
- [ ] Uptime check hitting /api/health/ every 1-5 minutes.
- [ ] Log retention configured (structured logs optional).

## Security
- [ ] DEBUG=false in production.
- [ ] No secrets in git history (git log -p -- .env* etc.). Rotate if discovered.
- [ ] CSP header tuned if loading external fonts/scripts (update CSP_HEADER env var).
- [ ] Rate limits (throttling) tuned for expected traffic.

## Frontend
- [ ] EXPO_PUBLIC_API_BASE points to production backend domain.
- [ ] Separate .env files for dev vs prod (not committed).
- [ ] Web build tested (expo export) and mobile clients point to correct API.

## CI/CD
- [ ] GitHub Actions CI passing (tests + build).
- [ ] (Optional) Docker image published to registry (tag with git SHA).

## Rollout
- [ ] Staging environment verified with same config class.
- [ ] Manual smoke tests: auth register/login, profile fetch, document create, chat.
- [ ] Rollback plan (previous image or backup) documented.

## Post-Deploy
- [ ] First 24h monitor error rate & latency.
- [ ] Schedule quarterly secret rotation.
- [ ] Document on-call escalation path.

---
Generated automatically to guide consistent and safe deployments.

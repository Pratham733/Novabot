# MongoDB Setup (Clean Restart)

## Option A: Provide Full URI (legacy style)
Set in `.env`:
```
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=novabot
```
If password has special chars, encode it (use Python: `quote_plus`).

## Option B (Recommended): Component Variables
```
MONGODB_USER=yourUser
MONGODB_PASSWORD=yourPassword123!
MONGODB_HOST=cluster0.xxxxx.mongodb.net
MONGODB_PARAMS=retryWrites=true&w=majority&appName=NovaBot
MONGODB_DB_NAME=novabot
```
Do NOT set `MONGODB_URI`; code will build a safe URI automatically with proper encoding.

## Steps
1. In Atlas: Create database user with readWriteAnyDatabase (dev) or scoped to `novabot`.
2. Add your IP to Network Access (or 0.0.0.0/0 temporarily for dev).
3. Fill `.env` with component vars.
4. Restart Django server.
5. Hit `/api/health/` → expect `mongo: ok`.
6. First document/chat insert will create DB & collections.

## Troubleshooting
- `bad auth`: wrong credentials or not yet propagated (wait 1–2 minutes) or using old user.
- `must be escaped`: you tried full URI with unencoded password; switch to component mode.
- DNS / timeout: cluster hostname typo or IP not whitelisted.

## Rotating Credentials
1. Create new user.
2. Update `.env` with new user/password.
3. Remove old user.
4. Restart server.


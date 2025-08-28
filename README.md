<div align="center">

# NovaBot

AI‑powered document generation & chat platform with a Django + DRF backend and a React Native / Expo frontend (kept as a Git submodule).

**Monorepo layout**

```
Novabot/                (this repo)
├─ backend/             Django REST API (auth, documents, chat, health)
├─ nova_bot/            Frontend (Expo / React Native) – submodule → Novabot_Frontend
├─ docker-compose.yml   Local dev orchestration (backend + MongoDB)
└─ .gitmodules          Submodule config for `nova_bot`
```

---
</div>

## ✨ Core Features
Backend (Django / DRF):
- JWT auth (SimpleJWT) + optional Firebase verification
- Document CRUD & regeneration endpoint (AI hook ready)
- Chat endpoint proxying OpenAI / Gemini (extensible)
- Dual storage: relational (SQLite/Postgres) + MongoDB for chat & document logs
- Health check (`/api/health/`) including Mongo & AI provider status
- Rate limiting (DRF throttles) & structured exception logging middleware

Frontend (Expo / React Native):
- Cross‑platform (iOS / Android / Web) via Expo Router
- Auth flows, document generator, file converter, history, settings
- Context-based state mgmt, custom UI kit, Tailwind style utilities
- Environment-driven API + AI provider config

Dev Tooling:
- `.env` driven configuration (backend & frontend)
- Docker Compose for backend + Mongo
- Submodule workflow for clean separation of frontend repo history

## 🧩 Submodule: Frontend
The frontend lives in its own repo: `Novabot_Frontend` and is linked here as `nova_bot` (git submodule).

Clone + init (first time):
```bash
git clone https://github.com/Pratham733/Novabot.git
cd Novabot
git submodule update --init --recursive
```

Pull latest later:
```bash
git pull
git submodule update --init --recursive --remote
```

Update the submodule pointer after pushing frontend changes:
```bash
cd nova_bot
# (make changes, commit, push)
git push
cd ..
git add nova_bot
git commit -m "chore: bump frontend submodule"
git push
```

## 🔧 Backend Quick Start
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
cp .env.example .env  # create & edit
python manage.py migrate
python manage.py runserver  # http://127.0.0.1:8000
```

Minimal backend `.env` (see `backend/README.md` for more):
```
DJANGO_SECRET_KEY=change-me
DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost
MONGODB_URI=mongodb://localdev:localdevpass@localhost:27017/?retryWrites=true&w=majority
MONGODB_DB_NAME=novabot
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
AI_DEFAULT_TEMPERATURE=0.7
```

Run with Docker (backend + Mongo):
```bash
docker compose up --build
# Backend: http://127.0.0.1:8000   Mongo: 27017
```

## 💻 Frontend Quick Start
```bash
git submodule update --init --recursive  # if not already
cd nova_bot
npm install  # or yarn
npm start    # Expo dev server
```

Frontend `.env` example (`nova_bot/.env`):
```
EXPO_PUBLIC_API_BASE=http://127.0.0.1:8000
EXPO_PUBLIC_AI_PROVIDER=openai
EXPO_PUBLIC_AI_MODEL=gpt-4o-mini
EXPO_PUBLIC_AI_TEMPERATURE=0.7
```
Firebase keys can be added similarly (see `nova_bot/README.md`).

## 📡 Key API Endpoints
```
POST /api/auth/register/
POST /api/auth/token/          (JWT obtain)
POST /api/auth/token/refresh/
GET  /api/auth/me/
GET|POST /api/documents/
GET|PATCH|DELETE /api/documents/<id>/
POST /api/documents/<id>/regenerate/
POST /api/chat/                (messages[])
GET  /api/health/
```

## 🧪 Development Tips
- Run `python manage.py test` inside `backend` (add tests under each app's `tests.py`).
- Use feature branches: `git checkout -b feature/<short-name>`.
- Keep secrets out of git (.env, Firebase JSON already ignored).

## 🚀 Deploy Overview
Backend (production):
1. Set `DEBUG=false`, proper `ALLOWED_HOSTS`, secure `DJANGO_SECRET_KEY`.
2. Provide `DATABASE_URL` (Postgres) & production Mongo connection.
3. Collect static files: `python manage.py collectstatic`.
4. Run via ASGI/WSGI server (gunicorn / uvicorn) behind reverse proxy.

Frontend:
1. Ensure `EXPO_PUBLIC_API_BASE` points to deployed backend.
2. Build web: `npm run build:web` or use Expo EAS for mobile binaries.

## 🔒 Security Highlights
- JWT + optional Firebase verification
- CORS controlled (auto-open in DEBUG; restrict in production)
- Whitenoise static serving + security headers middleware
- Throttle rates configurable via env (`THROTTLE_ANON`, `THROTTLE_USER`)

## 🗺 Roadmap (excerpt)
- OpenAPI / Swagger UI (drf-spectacular integration)
- Enhanced regeneration logic with AI provider abstraction
- Real-time collaboration & presence
- Multi-language document templates
- Rate limiting refinements & audit logging

## 🤝 Contributing
1. Fork & clone
2. `git submodule update --init --recursive`
3. Create a branch: `git checkout -b feature/<name>`
4. Commit in logical chunks (Conventional Commits encouraged)
5. Push & open PR

## 🧾 License
MIT (unless superseded by org policy) – see future `LICENSE`.

---
Made with ❤️  using Django, DRF, React Native, Expo & modern AI APIs.


# NovaBot Backend

Django + DRF backend for NovaBot (AI chatbot + smart document generator).

## Features
- JWT auth (SimpleJWT) with custom user (unique email, display name)
- Document CRUD & regenerate endpoint
- Chatbot endpoint proxying OpenAI API
- MongoDB (pymongo) for chat/document logs (hybrid storage)
- Health check (`/api/health/`) verifying Mongo & OpenAI
- Environment-driven settings via `.env`

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env  # then edit values
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Environment Variables (.env)
See `.env.example` for full list. Required minimal:
```
DJANGO_SECRET_KEY=...
DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority&appName=NovaBotDev
MONGODB_DB_NAME=novabot_dev
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
Optional:
```
AI_DEFAULT_TEMPERATURE=0.7
CORS_ALLOWED_ORIGINS=http://localhost:19006
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000
```

## Endpoints
- `GET /api/` API root
- `POST /api/auth/register/`
- `POST /api/auth/token/` & `POST /api/auth/token/refresh/`
- `GET /api/auth/me/`
- `GET/POST /api/documents/`
- `GET/PATCH/DELETE /api/documents/<id>/`
- `POST /api/documents/<id>/regenerate/`
- `POST /api/chat/` (messages: list of {role, content})
- `GET /api/health/`

## Health Check
`/api/health/` returns JSON with mongo/openai status and version.

## Regenerate Placeholder
Document regeneration currently appends a placeholder; integrate real AI logic in `documents.views.regenerate_document` using `services.ai.chat_complete`.

## Next Improvements
- Swagger / OpenAPI docs
- Firebase auth token verification
- Chat history listing & pagination
- Rate limiting & throttling
- Production settings (separate DEBUG, CORS)

## License
Internal / TBD.

from pathlib import Path
from datetime import timedelta
import os
try:  # Optional dependency; installed in production / when using Postgres
    import dj_database_url  # type: ignore
except ImportError:  # pragma: no cover
    dj_database_url = None  # type: ignore

from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-insecure-key')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',') if not DEBUG else ['*']
if not DEBUG and SECRET_KEY == 'dev-insecure-key':
    raise RuntimeError('Provide a secure DJANGO_SECRET_KEY in production')

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'drf_spectacular',
    'corsheaders',

    # Local apps
    'chatbot',
    'documents',
    'users',
]

# Middleware
MIDDLEWARE = [
    'novabot_backend.middleware.ExceptionLoggingMiddleware',
    'novabot_backend.middleware.SecurityHeadersMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # <-- must be first after SecurityMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    raw = os.getenv('CORS_ALLOWED_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = [o.strip() for o in raw.split(',') if o.strip()]
    CORS_ALLOW_ALL_ORIGINS = False
    # Optional: allow credentials if using cookie auth later
    CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [h for h in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if h]

# DRF & JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Throttling (can be tuned via env vars THROTTLE_ANON / THROTTLE_USER)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

ROOT_URLCONF = 'novabot_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'novabot_backend.wsgi.application'

# Database: use DATABASE_URL if provided, else fallback to SQLite
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    if dj_database_url is None:
        raise RuntimeError('dj-database-url not installed. Run: pip install dj-database-url')
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.getenv('DB_CONN_MAX_AGE', '60')),
            ssl_require=os.getenv('DB_SSL_REQUIRE', 'false').lower() == 'true'
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# MongoDB (used directly via pymongo for documents & chat logs)
# Preferred: supply components and let code build URI safely.
MONGODB_URI = os.getenv('MONGODB_URI')  # If provided, overrides component build
MONGODB_USER = os.getenv('MONGODB_USER')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')  # e.g. cluster0.xxxxx.mongodb.net
MONGODB_PARAMS = os.getenv('MONGODB_PARAMS', 'retryWrites=true&w=majority')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'novabot')
MONGODB_COLLECTION_DOCUMENTS = os.getenv('MONGODB_COLLECTION_DOCUMENTS', 'documents')
MONGODB_COLLECTION_CHATS = os.getenv('MONGODB_COLLECTION_CHATS', 'chat_sessions')
MONGODB_AUTH_SOURCE = os.getenv('MONGODB_AUTH_SOURCE', '')  # e.g., 'admin' or your DB name

# OpenAI / AI settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
AI_DEFAULT_TEMPERATURE = float(os.getenv('AI_DEFAULT_TEMPERATURE', '0.7'))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# DRF defaults
REST_FRAMEWORK.update({
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.getenv('THROTTLE_ANON', '60/min'),
        'user': os.getenv('THROTTLE_USER', '120/min'),
    }
})

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Application version (can be overridden via environment for deploy automation)
APP_VERSION = os.getenv('APP_VERSION', '0.1.0')

# If running behind a TLS terminator / reverse proxy (e.g., Caddy, nginx)
# trust X-Forwarded-Proto so Django knows the original scheme for redirects & CSRF
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Ensure Django uses the original Host header provided by the proxy
USE_X_FORWARDED_HOST = True

# Production security hardening
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'true').lower() == 'true'

# Optional Sentry error monitoring
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    try:  # dynamic import to avoid static import errors when package absent
        import importlib
        sentry_sdk = importlib.import_module('sentry_sdk')  # type: ignore
        django_integration_mod = importlib.import_module('sentry_sdk.integrations.django')  # type: ignore
        DjangoIntegration = getattr(django_integration_mod, 'DjangoIntegration')  # type: ignore
        sentry_sdk.init(  # type: ignore
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.0')),
            send_default_pii=False,
        )
    except Exception:
        # Silently ignore Sentry init issues (package missing or misconfigured)
        pass

SPECTACULAR_SETTINGS = {
    'TITLE': 'NovaBot API',
    'DESCRIPTION': 'API for NovaBot backend (auth, documents, chat, health).',
    'VERSION': APP_VERSION,
}

# Firebase (optional) - token verification setup
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON', '')  # path to service account JSON or JSON string
import base64
import tempfile

# Try to get base64-encoded credentials from env, else fallback to file path
FIREBASE_CREDENTIALS_B64 = os.environ.get("FIREBASE_CREDENTIALS_B64")
if FIREBASE_CREDENTIALS_B64:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        f.write(base64.b64decode(FIREBASE_CREDENTIALS_B64))
        FIREBASE_CREDENTIALS_JSON = f.name
else:
    FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON")

# If FIREBASE_PROJECT_ID is set, append FirebaseAuthentication
if FIREBASE_PROJECT_ID:
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
        'users.authentication.FirebaseAuthentication',
        *REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'],
    )

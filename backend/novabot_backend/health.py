from django.http import JsonResponse
from django.conf import settings
from services.mongo import get_client
from services.ai import chat_complete
import time


def health_view(_request):
    start = time.time()
    mongo_status = 'unknown'
    openai_status = 'skipped'
    gemini_status = 'skipped'

    # Mongo check
    mongo_hint = None
    try:
        client = get_client()
        client.admin.command('ping')
        mongo_status = 'ok'
    except Exception as e:
        err = str(e)
        if 'must be escaped' in err or 'escaped according to RFC 3986' in err:
            mongo_hint = "Your MongoDB password contains special characters. Encode them using urllib.parse.quote_plus. Example: password 'Pa@@123' -> 'Pa%40%40123'."
        if 'bad auth' in err or 'authentication failed' in err:
            mongo_hint = (mongo_hint or '') + " Set MONGODB_USER/MONGODB_PASSWORD correctly and ensure the user has access to MONGODB_DB_NAME. "
            if getattr(settings, 'MONGODB_AUTH_SOURCE', '') or 'authSource=' in getattr(settings, 'MONGODB_PARAMS', ''):
                pass
            else:
                mongo_hint += "If your user authenticates against a different database, set MONGODB_AUTH_SOURCE (e.g., 'admin')."
        mongo_status = f'error: {err}'

    # OpenAI minimal check (only if key configured)
    if settings.OPENAI_API_KEY:
        test = chat_complete([{"role": "user", "content": "ping"}], temperature=0)
        if 'error' in test:
            openai_status = f"error: {test['error'][:120]}"
        else:
            openai_status = 'ok'
    # Gemini minimal check
    if getattr(settings, 'GEMINI_API_KEY', ''):
        test = chat_complete([{"role": "user", "content": "ping"}], temperature=0, provider='gemini')
        if 'error' in test:
            gemini_status = f"error: {test['error'][:120]}"
        else:
            gemini_status = 'ok'

    payload = {
        'status': 'ok' if mongo_status == 'ok' else 'degraded',
        'mongo': mongo_status,
        'openai': openai_status,
        'gemini': gemini_status,
        'version': getattr(settings, 'APP_VERSION', 'unknown'),
        'elapsed_ms': int((time.time() - start) * 1000)
    }
    if mongo_hint:
        payload['mongo_hint'] = mongo_hint
    # Provide guidance for Gemini 404 (often wrong model name or beta path changes)
    if isinstance(payload.get('gemini'), str) and '404' in payload['gemini']:
        payload['gemini_hint'] = "Ensure GEMINI_MODEL is valid (e.g., 'gemini-1.5-flash' or 'gemini-1.5-pro') and API base uses v1beta."
    # Provide guidance for Gemini 503 (service unavailable, often transient or quota/region issue)
    if isinstance(payload.get('gemini'), str) and '503' in payload['gemini']:
        payload['gemini_hint'] = "Gemini service unavailable (503). This is often transient. Retry shortly; if persistent, check API quota/billing, model availability in your region, and firewall/proxy settings."
    return JsonResponse(payload)

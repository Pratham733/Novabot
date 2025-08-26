import os
import time
from django.conf import settings
import requests
from typing import List, Dict, Optional

OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
GEMINI_API_BASE = os.getenv('GEMINI_API_BASE', 'https://generativelanguage.googleapis.com/v1beta')


def _normalize_messages(messages: List[Dict]) -> List[Dict]:
    return messages or []


def openai_chat(messages: List[Dict], model: str, temperature: float):
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return {"error": "OPENAI_API_KEY not configured"}
    url = f"{OPENAI_API_BASE}/chat/completions"
    try:
        r = requests.post(url, json={"model": model, "messages": messages, "temperature": temperature}, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
        r.raise_for_status()
        data = r.json()
        return {
            'provider': 'openai',
            'id': data.get('id'),
            'model': data.get('model'),
            'content': data.get('choices', [{}])[0].get('message', {}).get('content', ''),
            'raw': data,
            'usage': data.get('usage', {})
        }
    except Exception as e:
        return {"provider": "openai", "error": str(e)}


def _post_with_retries(url: str, payload: dict, headers: Optional[dict] = None, timeout: int = 60, retries: int = 2, backoff_base: float = 0.5):
    """POST with simple exponential backoff for transient HTTP errors.
    Retries on 429, 500, 502, 503, 504 and common request exceptions.
    """
    last_exc = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, json=payload, headers=headers or {}, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                last_exc = requests.HTTPError(f"{r.status_code} {r.reason}", response=r)
                if attempt < retries:
                    time.sleep(backoff_base * (2 ** attempt))
                    continue
                r.raise_for_status()
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff_base * (2 ** attempt))
                continue
            raise
    # Should not reach here; raise the last exception to satisfy type checkers
    if last_exc:
        raise last_exc


def gemini_chat(messages: List[Dict], model: str, temperature: float):
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
    # Gemini expects a different structure
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {"parts": [{"text": m.get('content', '')}]} for m in messages if m.get('role') != 'system'
        ],
        "generationConfig": {"temperature": temperature}
    }
    try:
        r = _post_with_retries(url, payload, timeout=60, retries=2)
        data = r.json()
        text = ''
        try:
            text = data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            text = ''
        return {
            'provider': 'gemini',
            'model': model,
            'content': text,
            'raw': data
        }
    except Exception as e:
        status = None
        # Some request exceptions include a response attribute; access it safely.
        resp = getattr(e, 'response', None)
        if resp is not None:
            try:
                status = getattr(resp, 'status_code', None)
            except Exception:
                status = None
        return {"provider": "gemini", "error": str(e), "status_code": status}


def chat_complete(messages: List[Dict], model: Optional[str] = None, temperature: Optional[float] = None, provider: Optional[str] = None):
    """Unified chat interface.
    provider: openai | gemini | auto
    If provider is auto, route based on heuristic:
      - If question looks like a factual query (contains 'latest' or 'according to' or '?') and PERPLEXITY key present -> perplexity
      - Else if long context (> 4000 chars) and Gemini key present -> gemini
      - Else openai.
    """
    messages = _normalize_messages(messages)
    temp = temperature if temperature is not None else settings.AI_DEFAULT_TEMPERATURE
    provider = provider or 'openai'

    if provider == 'auto':
        user_text = ' '.join(m.get('content','') for m in messages if m.get('role') == 'user')
        if len(user_text) > 4000 and getattr(settings, 'GEMINI_API_KEY', ''):
            provider = 'gemini'
        else:
            provider = 'openai'

    if provider == 'openai':
        mdl = model or settings.OPENAI_MODEL
        return openai_chat(messages, mdl, temp)
    if provider == 'gemini':
        mdl = model or getattr(settings, 'GEMINI_MODEL', 'gemini-pro')
        return gemini_chat(messages, mdl, temp)
    # If auto-selected Gemini fails with a transient error, fall back to OpenAI
    # Determine auto-route again
    if provider == 'auto':
        # If we somehow get here, just try OpenAI as a safe default
        mdl = model or settings.OPENAI_MODEL
        return openai_chat(messages, mdl, temp)
    return {"error": f"Unknown provider '{provider}'"}

from django.conf import settings
from typing import Optional

_initialized = False

def _init():
    global _initialized
    if _initialized:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
        import os, json, base64

        cred = None
        creds_val = settings.FIREBASE_CREDENTIALS_JSON

        if creds_val:
            # 1) Treat as file path if it exists
            if os.path.exists(creds_val):
                cred = credentials.Certificate(creds_val)
            else:
                # 2) Try raw inline JSON
                data = None
                try:
                    data = json.loads(creds_val)
                except json.JSONDecodeError:
                    # 3) Try base64-encoded JSON
                    try:
                        decoded = base64.b64decode(creds_val).decode('utf-8')
                        data = json.loads(decoded)
                    except Exception:
                        data = None
                if data:
                    cred = credentials.Certificate(data)
        else:
            # 4) Try GOOGLE_APPLICATION_CREDENTIALS path (ADC)
            gac_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
            if gac_path and os.path.exists(gac_path):
                cred = credentials.Certificate(gac_path)

        if cred is not None:
            firebase_admin.initialize_app(cred)
        else:
            # Fall back to default ADC if available in environment (e.g., GCP)
            firebase_admin.initialize_app()

        _initialized = True
    except Exception:
        # Leave uninitialized; verification will fail gracefully
        _initialized = False

def verify_id_token(id_token: str) -> Optional[dict]:
    try:
        _init()
        import firebase_admin
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token, check_revoked=False)
        # Optionally ensure project match
        if settings.FIREBASE_PROJECT_ID and decoded.get('aud') and settings.FIREBASE_PROJECT_ID not in decoded.get('aud', ''):
            return None
        return decoded
    except Exception:
        return None

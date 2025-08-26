from rest_framework.authentication import BaseAuthentication, get_authorization_header
from django.contrib.auth import get_user_model
from typing import Optional, Tuple, Any
from services.firebase_auth import verify_id_token

User = get_user_model()

class FirebaseAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request) -> Optional[Tuple[Any, None]]:
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        if len(auth) == 1:
            return None
        token = auth[1].decode()
        payload = verify_id_token(token)
        if not payload:
            return None
        uid = payload.get('uid') or payload.get('user_id')
        email = payload.get('email')
        defaults = {}
        if email:
            defaults['email'] = email
        user, _ = User.objects.get_or_create(username=uid or email or f'user_{payload.get("sub")}', defaults=defaults)
        return (user, None)

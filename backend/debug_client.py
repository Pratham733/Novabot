import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novabot_backend.settings')
django.setup()

from django.test import Client

c = Client()
try:
    resp = c.post('/api/chat/', json.dumps({'messages':[{'role':'user','content':'test from client'}]}), content_type='application/json')
    print('status', resp.status_code)
    print('content:', resp.content.decode('utf-8'))
except Exception as e:
    import traceback
    traceback.print_exc()

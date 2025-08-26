import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novabot_backend.settings')
django.setup()

from services.ai import chat_complete
from services.mongo import chats_collection
from django.utils import timezone


def run_test():
    messages = [{'role': 'user', 'content': 'hello from debug script'}]
    print('Calling chat_complete...')
    try:
        resp = chat_complete(messages)
        print('chat_complete response:')
        print(json.dumps(resp, indent=2, default=str))
    except Exception as e:
        print('chat_complete raised:')
        import traceback
        traceback.print_exc()
        return

    print('Attempting to write to Mongo...')
    record = {
        'user_id': 0,
        'username': 'debugger',
        'messages': messages,
        'provider': resp.get('provider') if isinstance(resp, dict) else 'unknown',
        'response': resp,
        'created_at': timezone.now().isoformat(),
    }
    try:
        coll = chats_collection()
        r = coll.insert_one(record)
        print('Inserted chat id:', str(r.inserted_id))
    except Exception as e:
        print('Mongo insert raised:')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_test()

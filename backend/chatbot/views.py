from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from services.ai import chat_complete
from services.mongo import chats_collection
from django.utils import timezone
import os


class ChatbotView(APIView):
	# Temporarily allow any for debugging; revert to IsAuthenticated after diagnosis
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		# Top-level guard: catch any unexpected exception and return a diagnostic JSON
		try:
			# lightweight file-based trace for debugging HTTP path
			try:
				with open('view-debug.log', 'a', encoding='utf-8') as _f:
					_f.write(f"Entered ChatbotView.post at {timezone.now().isoformat()} user={getattr(request.user, 'username', None)}\n")
			except Exception:
				# ignore logging failures
				pass
			user = request.user
			messages = request.data.get('messages') or []
			if not isinstance(messages, list):
				return Response({'error': 'messages must be a list'}, status=400)
			# Basic normalization & caps to avoid oversized payloads
			norm_msgs = []
			for m in messages[:20]:  # cap to last 20 messages
				if not isinstance(m, dict):
					continue
				role = m.get('role')
				content = (m.get('content') or '')
				if role not in ['user', 'assistant', 'system']:
					continue
				norm_msgs.append({'role': role, 'content': str(content)[:8000]})
			provider = request.data.get('provider') or 'openai'  # openai | gemini | auto
			model = request.data.get('model')
			temperature = request.data.get('temperature')
			try:
				temperature = float(temperature) if temperature is not None else None
			except (TypeError, ValueError):
				temperature = None
			# Call AI service with defensive error handling so a provider failure doesn't 500
			ai_response = None
			try:
				ai_response = chat_complete(norm_msgs, model=model, temperature=temperature, provider=provider)
			except Exception as e:
				# Log and return a helpful error blob instead of crashing
				import traceback, logging
				logging.exception('AI provider error')
				ai_response = {'error': f'AI provider error: {str(e)}', 'trace': traceback.format_exc()}
			# Prepare record and attempt to persist chat; handle Mongo errors gracefully
			record = {
				'user_id': user.id,
				'username': user.username,
				'messages': norm_msgs,
				'provider': provider or 'auto',
				'response': ai_response,
				'created_at': timezone.now().isoformat(),
			}
			try:
				# mark before Mongo access
				try:
					with open('view-debug.log', 'a', encoding='utf-8') as _f:
						_f.write(f"Before Mongo access at {timezone.now().isoformat()}\n")
				except Exception:
					pass
				# immediate checkpoint after before-mongo
				try:
					with open('view-debug.log', 'a', encoding='utf-8') as _f:
						_f.write("checkpoint_after_before_mongo\n")
				except Exception:
					pass
				# Optionally skip Mongo writes for HTTP requests to isolate issues
				# Debug: log SKIP_MONGO_HTTP and record snapshot
				try:
					with open('view-debug.log', 'a', encoding='utf-8') as _f:
						_f.write(f"SKIP_MONGO_HTTP={os.getenv('SKIP_MONGO_HTTP', 'unset')} record_keys={list(record.keys())}\n")
				except Exception:
					pass
				if os.getenv('SKIP_MONGO_HTTP', '1') == '1':
					try:
						with open('view-debug.log', 'a', encoding='utf-8') as _f:
							_f.write(f"Skipping Mongo write due to SKIP_MONGO_HTTP=1 at {timezone.now().isoformat()}\n")
					except Exception:
						pass
					# indicate skipped in record and avoid DB access
					record['mongo_error'] = 'skipped-by-SKIP_MONGO_HTTP'
				else:
					coll = chats_collection()
					try:
						r = coll.insert_one(record)
						# attach inserted id as string to avoid ObjectId serialization errors
						try:
							record['_id'] = str(r.inserted_id)
						except Exception:
							pass
						# post-insert debug mark
						try:
							with open('view-debug.log', 'a', encoding='utf-8') as _f:
								_f.write(f"After Mongo insert at {timezone.now().isoformat()} inserted_id={record.get('_id')}\n")
						except Exception:
							pass
					except Exception as e:
						# attach mongo error but still return the AI response
						record['mongo_error'] = str(e)
						import logging
						logging.exception('Mongo insert error')
			except Exception as e:
				# If obtaining the collection fails (bad URI, auth), don't 500
				record['mongo_error'] = f'Failed to access chats collection: {str(e)}'
				import logging
				logging.exception('Mongo access error')
			# Ensure the record is JSON-serializable: recursively stringify unknown types
			def _sanitize(obj):
				if isinstance(obj, (str, int, float, bool)) or obj is None:
					return obj
				if isinstance(obj, dict):
					return {k: _sanitize(v) for k, v in obj.items()}
				if isinstance(obj, list):
					return [_sanitize(v) for v in obj]
				# fallback: stringify unknown types (ObjectId, datetimes, bytes, etc.)
				try:
					return str(obj)
				except Exception:
					return None
			safe_record = _sanitize(record)
			try:
				return Response(safe_record)
			except Exception as e:
				try:
					with open('view-debug.log', 'a', encoding='utf-8') as _f:
						_f.write(f"Response serialization failed at {timezone.now().isoformat()}: {str(e)}\n")
				except Exception:
					pass
				return Response({'error': 'serialization_failed', 'detail': str(e)}, status=500)
		except Exception as e:
			# Catch any unexpected/unhandled exception and return trace to client for diagnostics
			import traceback, logging
			logging.exception('Unhandled exception in ChatbotView.post')
			return Response({'error': 'unhandled_exception', 'detail': str(e), 'trace': traceback.format_exc()}, status=500)


class ChatHistoryView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		coll = chats_collection()
		try:
			limit = int(request.GET.get('limit', 50))
		except ValueError:
			limit = 50
		limit = max(1, min(limit, 200))
		query = {'user_id': request.user.id}
		before = request.GET.get('before')
		if before:
			# 'created_at' stored as ISO-8601 string; lexical order matches chronological
			query['created_at'] = {'$lt': before}
		cursor = coll.find(query).sort('created_at', -1).limit(limit)
		items = []
		for c in cursor:
			c['_id'] = str(c.get('_id'))
			items.append({k: c[k] for k in c if k not in ['raw']})  # omit raw provider payload
		return Response({'results': items, 'count': len(items), 'limit': limit, 'before': before})

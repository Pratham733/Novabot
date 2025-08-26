from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer
from services.mongo import profiles_collection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from services.firebase_auth import verify_id_token

User = get_user_model()


class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		return self.request.user

class ProfileView(generics.GenericAPIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		coll = profiles_collection()
		doc = coll.find_one({'user_id': request.user.id}) or {}
		doc['_id'] = str(doc.get('_id', ''))
		return Response(doc)

	def post(self, request):
		coll = profiles_collection()
		data = {k: v for k, v in request.data.items() if k in ['display_name', 'bio', 'avatar']}
		data['user_id'] = request.user.id
		coll.update_one({'user_id': request.user.id}, {'$set': data}, upsert=True)
		doc = coll.find_one({'user_id': request.user.id}) or {}
		doc['_id'] = str(doc.get('_id', ''))
		return Response(doc)


class ApiRootView(APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request, format=None):
		return Response({
			'register': request.build_absolute_uri(reverse('auth-register')),
			'token': request.build_absolute_uri(reverse('token_obtain_pair')),
			'token_refresh': request.build_absolute_uri(reverse('token_refresh')),
			'me': request.build_absolute_uri(reverse('auth-me')),
		})


class FirebaseExchangeView(APIView):
	"""Exchange a Firebase ID token for backend JWT access/refresh tokens.
	This allows the frontend to sign in with Firebase and then receive backend JWTs
	compatible with rest_framework_simplejwt.
	"""
	permission_classes = [AllowAny]

	def post(self, request):
		id_token = request.data.get('id_token')
		if not id_token:
			return Response({'detail': 'id_token required'}, status=status.HTTP_400_BAD_REQUEST)
		payload = verify_id_token(id_token)
		if not payload:
			return Response({'detail': 'Invalid Firebase token'}, status=status.HTTP_401_UNAUTHORIZED)
		uid = payload.get('uid') or payload.get('user_id') or payload.get('sub')
		email = payload.get('email')
		defaults = {}
		if email:
			defaults['email'] = email
		user, _ = User.objects.get_or_create(username=uid or email or f'user_{payload.get("sub")}', defaults=defaults)
		refresh = RefreshToken.for_user(user)
		return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, ApiRootView, ProfileView
from .views import FirebaseExchangeView

urlpatterns = [
    path('', ApiRootView.as_view(), name='api-root'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    # Alias for convenience: /api/users/me/ -> MeView
    path('users/me/', MeView.as_view(), name='users-me'),
    path('auth/firebase/', FirebaseExchangeView.as_view(), name='auth-firebase-exchange'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

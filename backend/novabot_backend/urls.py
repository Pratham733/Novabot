"""
URL configuration for novabot_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse, HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from .health import health_view


def root_view(_request):
    """Lightweight index describing available top-level API endpoints."""
    return JsonResponse({
        'message': 'NovaBot API',
        'version': getattr(settings, 'APP_VERSION', None),
        'endpoints': {
            'admin': '/admin/',
            'api_root': '/api/',
            'api_v1_root': '/api/v1/',  # version alias pointing to same routes (future-proof)
            'health': '/api/health/',
            'schema': '/api/schema/',
            'docs': '/api/docs/',
            'auth': {
                'register': '/api/auth/register/',
                'token': '/api/auth/token/',
                'token_refresh': '/api/auth/token/refresh/',
                'me': '/api/auth/me/',
            },
            'documents': {
                'list_create': '/api/documents/',
                'detail': '/api/documents/{id}/',
                'regenerate': '/api/documents/{id}/regenerate/',
                'finalize': '/api/documents/{id}/finalize/',
                'convert': '/api/documents/convert/',
                'converted_files': '/api/converted/',
            },
            'chat': {
                'chat': '/api/chat/',
                'history': '/api/chat/history/',
            }
        }
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    # Unversioned (legacy) API paths
    path('api/', include('users.urls')),
    path('api/', include('documents.urls')),
    path('api/', include('chatbot.urls')),
    # Versioned alias (v1) – currently identical includes for forward compatibility
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('documents.urls')),
    path('api/v1/', include('chatbot.urls')),
    path('api/health/', health_view, name='health'),
    # API schema & docs (unversioned for now)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    # Basic static hints to reduce 404 noise in dev
    re_path(r'^favicon\.ico$', lambda r: HttpResponse(status=204)),
    re_path(r'^robots\.txt$', lambda r: HttpResponse('User-agent: *\nDisallow:', content_type='text/plain')),
]

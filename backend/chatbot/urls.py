from django.urls import path
from .views import ChatbotView, ChatHistoryView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chatbot-chat'),
    path('chat/history/', ChatHistoryView.as_view(), name='chatbot-history'),
]

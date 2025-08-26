from django.urls import path
from .views import DocumentListCreateView, DocumentDetailView, regenerate_document, finalize_document, generate_document, export_document, convert_document, convert_capabilities, ConvertedFileListView

urlpatterns = [
    path('documents/', DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/regenerate/', regenerate_document, name='document-regenerate'),
    path('documents/<int:pk>/finalize/', finalize_document, name='document-finalize'),
    path('documents/generate/', generate_document, name='document-generate'),
    path('documents/<int:pk>/export/', export_document, name='document-export'),
    path('documents/convert/', convert_document, name='document-convert'),
    path('documents/convert/capabilities/', convert_capabilities, name='document-convert-capabilities'),
    path('converted/', ConvertedFileListView.as_view(), name='converted-file-list'),
]

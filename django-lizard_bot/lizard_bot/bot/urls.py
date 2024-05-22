from django.urls import path
from .views import FileListView

urlpatterns = [
    path('files/', FileListView.as_view(), name='file-list')
]
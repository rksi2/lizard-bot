from django.urls import path
from .views import FileListView, ServiceView, ScheduleTeacherView

urlpatterns = [
    path("files/", FileListView.as_view(), name="file-list"),
    path("service/", ServiceView.as_view(), name="service"),
    path("teachers/", ScheduleTeacherView.as_view(), name="teacher"),
]

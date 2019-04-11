from django.urls import path

from subject_area.views import SubjectAreaCreateView, SubjectAreaListView, SubjectAreaUpdateView

urlpatterns = [
    path("new/", SubjectAreaCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", SubjectAreaUpdateView.as_view(), name="edit"),
    path("", SubjectAreaListView.as_view(), name="list")
]

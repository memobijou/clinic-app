from django.urls import path

from subject_area.views import SubjectAreaCreateView, SubjectAreaListView, SubjectAreaUpdateView, CreateCategoryView, \
    UpdateCategoryView, CategoryDeleteView

urlpatterns = [
    path("new/", SubjectAreaCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", SubjectAreaUpdateView.as_view(), name="edit"),
    path("", SubjectAreaListView.as_view(), name="list"),
    path("<int:pk>/categories/new", CreateCategoryView.as_view(), name="new-category"),
    path("<int:pk>/categories/<int:category_pk>/edit", UpdateCategoryView.as_view(), name="edit-category"),
    path("<int:pk>/categories/<int:category_pk>/delete", CategoryDeleteView.as_view(), name="delete-category")
]

from django.urls import path
from rest_framework.routers import DefaultRouter
from subject_area.datatables import SubjectAreaDatatables
from subject_area.viewsets import SubjectAreaViewSet, CategoryViewSet
from django.urls import include


router = DefaultRouter(trailing_slash=False)
router.register("subject-areas", SubjectAreaViewSet)

categories_router = DefaultRouter(trailing_slash=False)
categories_router.register("categories", CategoryViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(categories_router.urls)),
    path(r'subject-areas-datatables/', SubjectAreaDatatables.as_view(), name="subject_area_datatables"),
]

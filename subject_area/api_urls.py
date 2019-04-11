from django.urls import path
from rest_framework.routers import DefaultRouter
from subject_area.datatables import SubjectAreaDatatables
from subject_area.viewsets import SubjectAreaViewSet
from django.urls import include


router = DefaultRouter(trailing_slash=False)
router.register("subject-areas", SubjectAreaViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'subject-areas-datatables/', SubjectAreaDatatables.as_view(), name="subject_area_datatables"),
]

from django.urls import path, include

from accomplishment.serializers import AccomplishmentViewSet, UserAccomplishmentViewSet
from accomplishment.datatables import AccomplishmentDatatables
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
from accomplishment.views import AccomplishmentListView, AccomplishmentUpdateView

router = routers.DefaultRouter()
router.register(r'accomplishments', AccomplishmentViewSet)
router.register(r'users', UserAccomplishmentViewSet)


urlpatterns = [
    path(r'api/', include(router.urls)),
    path(r'api/users/', include(router.urls)),
    path(r'datatables', AccomplishmentDatatables.as_view(), name="datatables"),
    path(r"", AccomplishmentListView.as_view(), name="list"),
    path(r"<int:pk>/edit", AccomplishmentUpdateView.as_view(), name="edit")
]


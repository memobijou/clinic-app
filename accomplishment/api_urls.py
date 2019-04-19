from django.urls import path, include
from accomplishment.viewsets import AccomplishmentViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'accomplishments', AccomplishmentViewSet, basename="accomplishment")


urlpatterns = [
    path(r'users/<int:user_id>/', include(router.urls)),
]

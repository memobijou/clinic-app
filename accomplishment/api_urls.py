from django.urls import path, include
from accomplishment.serializers import AccomplishmentViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'accomplishments', AccomplishmentViewSet)


urlpatterns = [
    path(r'users/<int:user_id>/', include(router.urls)),
]

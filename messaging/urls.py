from django.urls import include, path
from account.serializers import UserViewSet
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
from messaging.serializers import TextMessageViewset

router = routers.DefaultRouter()
router.register(r'messaging', TextMessageViewset)
# router.register(r'groups', GroupViewSet)


urlpatterns = [
    path(r'api/<int:user1>/<int:user2>/', include(router.urls)),
]
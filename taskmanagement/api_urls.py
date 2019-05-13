from rest_framework import routers
from taskmanagement.viewsets import TaskViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'tasks', TaskViewSet, basename="taskmanagement")

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'users/<int:user_id>/', include(router.urls)),

]

from django.urls import path, include
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
from taskmanagement.serializers import GroupTaskViewSet, GroupTaskDatatables
from taskmanagement.views import TaskListView, GroupTaskDetailView, TaskCreateView, UserTaskCreateView

group_task_router = routers.DefaultRouter()
group_task_router.register(r'', GroupTaskViewSet)


urlpatterns = [
    path(r'api/', include(group_task_router.urls)),
    path(r'', TaskListView.as_view(), name="tasks_list"),
    path(r'<int:pk>/edit/', GroupTaskDetailView.as_view(), name='edit_task'),
    path(r'group-task/datatables', GroupTaskDatatables.as_view(), name="group_task_datatables"),
    path(r'group-task/new/', TaskCreateView.as_view(), name="new_task"),
    path(r'group/<int:group_pk>/task/<int:task_pk>/new/users', UserTaskCreateView.as_view(), name="new_task_users"),
]

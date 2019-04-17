from django.urls import path, include
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
from taskmanagement.serializers import GroupTaskViewSet, TaskDatatables, UserTaskViewSet
from taskmanagement.views import TaskListView, TaskCreateView, UserTaskUpdateView, TaskDetailView

group_task_router = routers.DefaultRouter()
group_task_router.register(r'', GroupTaskViewSet)
user_task_router = routers.DefaultRouter()
user_task_router.register(r"", UserTaskViewSet)

urlpatterns = [
    path(r'api/', include(group_task_router.urls)),
    path(r'usertask/api/', include(user_task_router.urls)),
    path(r'', TaskListView.as_view(), name="tasks_list"),
    path(r'<int:pk>/edit/', TaskDetailView.as_view(), name='edit_task'),
    path(r'group-task/datatables', TaskDatatables.as_view(), name="group_task_datatables"),
    path(r'group-task/new/', TaskCreateView.as_view(), name="new_task"),
    path(r'group/<int:group_pk>/task/<int:task_pk>/new/users', UserTaskUpdateView.as_view(), name="new_task_users"),
]

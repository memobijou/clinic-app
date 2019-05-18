from django.urls import path
from taskmanagement.datatables import TaskDatatables
from taskmanagement.views import TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    path(r'', TaskListView.as_view(), name="tasks_list"),
    path(r'<int:pk>/edit/', TaskUpdateView.as_view(), name='edit_task'),
    path(r'group-task/datatables', TaskDatatables.as_view(), name="group_task_datatables"),
    path(r'group-task/new/', TaskCreateView.as_view(), name="new_task"),
    path(r'delete', TaskDeleteView.as_view(), name="delete_task"),
]

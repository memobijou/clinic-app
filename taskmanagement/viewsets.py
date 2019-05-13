from django.core.exceptions import MultipleObjectsReturned
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from taskmanagement.models import Task, UserTask
from taskmanagement.serializers import TaskSerializer, EndUserTaskSerializer
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class TaskViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user_id"] = self.kwargs.get("user_id")
        return context

    def get_queryset(self):
        if self.kwargs.get("user_id"):
            self.queryset = self.queryset.filter(users__id=self.kwargs.get("user_id")).distinct()
        if self.request.GET.get("sort") == "new":
            self.queryset = self.queryset.order_by("-id")
        elif self.request.GET.get("sort") == "deadline":
            self.queryset = self.queryset.order_by("end_datetime")
        return self.queryset

    @transaction.atomic
    @action(detail=True, methods=['PUT'])
    def completing(self, request, user_id=None, pk=None):
        try:
            instance = get_object_or_404(UserTask, task_id=pk, user_id=user_id)
        except MultipleObjectsReturned:
            return Response({"error": "Dem Nutzer wurde die Aufgabe mehrfach zugewiesen. "
                                      "Einem Nutzer darf die selbe Aufgabe nur einmal zugewiesen werden."},
                            status=status.HTTP_400_BAD_REQUEST)
        data = {**request.data, "completed": True}
        serializer = EndUserTaskSerializer(instance=instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, methods=['PUT'])
    def terminating(self, request, user_id=None, pk=None):
        try:
            instance = get_object_or_404(UserTask, task_id=pk, user_id=user_id)
        except MultipleObjectsReturned:
            return Response({"error": "Dem Nutzer wurde die Aufgabe mehrfach zugewiesen. "
                                      "Ein Nutzer darf dieselbe Aufgabe nur einmal zugewiesen bekommen."},
                            status=status.HTTP_400_BAD_REQUEST)
        data = {**request.data, "completed": None}
        serializer = EndUserTaskSerializer(instance=instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTaskViewSet(viewsets.ModelViewSet):
    queryset = UserTask.objects.all()
    serializer_class = EndUserTaskSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.filter_by_user_id()
        self.filter_by_task_id()
        return self.queryset

    def filter_by_user_id(self):
        user_ids = self.request.GET.getlist("user_id")

        if len(user_ids) > 0:
            self.queryset = self.queryset.filter(user__id__in=user_ids)

    def filter_by_task_id(self):
        task_ids = self.request.GET.getlist("task_id")

        if len(task_ids) > 0:
            self.queryset = self.queryset.filter(task__id__in=task_ids)

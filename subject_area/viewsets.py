from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin

from subject_area.models import SubjectArea, Category
from subject_area.serializers import SubjectAreaSerializer, CategorySerializer


class SubjectAreaViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = SubjectAreaSerializer
    queryset = SubjectArea.objects.all()

    def get_serializer_context(self):
        return {"user_id": self.request.query_params.get('user_id')}


class CategoryViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        if self.request.query_params.get('user_id'):
            return self.queryset.filter(subject_area__profiles__user_id=self.request.query_params.get('user_id'))
        else:
            return self.queryset

    def get_serializer_context(self):
        return {"user_id": self.request.query_params.get('user_id')}

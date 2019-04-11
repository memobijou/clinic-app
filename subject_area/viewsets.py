from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin

from subject_area.models import SubjectArea
from subject_area.serializers import SubjectAreaSerializer


class SubjectAreaViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = SubjectAreaSerializer
    queryset = SubjectArea.objects.all()

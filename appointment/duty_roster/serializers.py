from rest_framework import serializers, viewsets
# Serializers define the API representation.
from rest_framework.pagination import LimitOffsetPagination
from appointment.models import DutyRoster


class DutyRosterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DutyRoster
        fields = ('pk','upload_date', "file", "calendar_week",)


# ViewSets define the view behavior.
class DutyRosterViewSet(viewsets.ModelViewSet):
    queryset = DutyRoster.objects.all()
    serializer_class = DutyRosterSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset()

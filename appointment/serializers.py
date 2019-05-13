from rest_framework import serializers
from account.group.serializers import GroupSerializer
from appointment.models import Appointment


# Serializers define the API representation.
class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)
    promoter = serializers.StringRelatedField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    def get_start(self, instance):
        return instance.start_date

    def get_end(self, instance):
        return instance.end_date

    def get_title(self, instance):
        return instance.topic

    class Meta:
        model = Appointment
        fields = ('pk', 'topic', 'description', 'start_date', 'end_date', "place", "promoter", "is_infobox",
                  "is_conference", "groups", "title", "start", "end",)

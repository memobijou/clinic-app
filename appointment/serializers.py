from rest_framework import serializers
from account.group.serializers import GroupSerializer
from appointment.models import Appointment
from account.models import Group


# Serializers define the API representation.
class AppointmentSerializer(serializers.ModelSerializer):
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
        fields = ('pk', 'topic', 'description', 'start_date', 'end_date', "place", "promoter",
                  "groups", "title", "start", "end",)


class CalendarGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("pk", 'name', "color",)


class CalendarAppointmentSerializer(serializers.ModelSerializer):
    groups = CalendarGroupSerializer(many=True)
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
        fields = ('pk', 'topic', 'description', 'start_date', 'end_date', "place", "promoter",
                  "title", "start", "end", "groups")

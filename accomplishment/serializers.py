from rest_framework import serializers
from accomplishment.models import Accomplishment, UserAccomplishment
from account.serializers import UserSerializer


class AccomplishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accomplishment
        fields = ("pk", "name", "full_score", )


class UserAccomplishmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    accomplishment = AccomplishmentSerializer(read_only=True)
    completed = serializers.NullBooleanField(read_only=True)

    class Meta:
        model = UserAccomplishment
        fields = ('score', 'user', "accomplishment", "completed", )

    def validate_score(self, value):
        if value > self.instance.accomplishment.full_score:
            raise serializers.ValidationError(
                "Die Gesamtpunktezahl wurde erreicht und kann nicht mehr weiter erhöht werden.")
        elif value < 0:
            raise serializers.ValidationError("Die Punktezahl kann nicht kleiner als 0 sein.")
        return value

from rest_framework import serializers

from poll.models import Poll, Option


class OptionSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ("pk", "title", "selected")

    def get_selected(self, instance: Option):
        user_id = self.context.get("user_id")
        if user_id:
            user_option = instance.useroption_set.filter(user_id=user_id).first()

            if user_option:
                return user_option.selected


class PollSerializer(serializers.ModelSerializer):
    option_set = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ("title", "description", "open", "option_set", "created_datetime",)

from rest_framework import serializers

from poll.models import Poll, Option


class OptionSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ("pk", "title", "selected", "percentage",)

    def get_selected(self, instance: Option):
        user_id = self.context.get("user_id")
        if user_id:
            user_option = instance.useroption_set.filter(user_id=user_id).first()

            if user_option:
                return user_option.selected

    def get_percentage(self, instance):
        user_id = self.context.get("user_id")
        if user_id:
            user_options_count = instance.useroption_set.count()

            if user_options_count:
                return int((user_options_count/user_options_count)*100)
        return 0


class PollSerializer(serializers.ModelSerializer):
    option_set = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ("pk", "title", "description", "open", "option_set", "created_datetime",)

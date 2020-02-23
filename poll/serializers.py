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
        all_user_options_count = 0
        for option in instance.poll.option_set.all():
            for _ in option.useroption_set.all():
                all_user_options_count += 1
        user_id = self.context.get("user_id")
        if all_user_options_count == 0:
            return
        if user_id:
            # user_options_count = instance.useroption_set.filter(user_id=user_id).count()
            user_options_count = instance.useroption_set.filter().count()

            if user_options_count:
                return int((user_options_count/all_user_options_count)*100)
            else:
                return int((user_options_count/all_user_options_count)*100)
        return 0


class PollSerializer(serializers.ModelSerializer):
    option_set = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ("pk", "title", "description", "open", "option_set", "created_datetime",)

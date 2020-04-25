from rest_framework import serializers

from poll.models import Poll, Option, UserOption


class OptionSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ("pk", "title", "selected", "percentage", "participants_count",)

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
            return 0
        if user_id:
            user_options_count = instance.useroption_set.all().count()

            if user_options_count == 0:
                return 0

            if user_options_count:
                return int((user_options_count/all_user_options_count)*100)
            else:
                return int((user_options_count/all_user_options_count)*100)
        return 0

    def get_participants_count(self, instance: Option):
        total = UserOption.objects.filter(option__poll=instance.poll, selected=True).distinct().count()
        useroptions_count = 0
        for _ in instance.useroption_set.filter(selected=True):
            useroptions_count += 1
        return f'{useroptions_count}/{total}'


class PollSerializer(serializers.ModelSerializer):
    option_set = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ("pk", "title", "description", "open", "option_set", "created_datetime",)

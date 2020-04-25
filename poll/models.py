from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Poll(models.Model):
    class Meta:
        ordering = ("-pk",)

    title = models.CharField(max_length=200, null=True, blank=True, verbose_name="Bezeichnung")
    description = models.TextField(null=True, blank=True, verbose_name="Beschreibung")
    created_datetime = models.DateTimeField(null=True, auto_now=True)
    open = models.BooleanField(default=False, verbose_name="Veröffentlichen")


class Option(models.Model):
    class Meta:
        ordering = ("pk",)

    title = models.CharField(max_length=200, verbose_name="Bezeichnung")
    poll = models.ForeignKey("poll.Poll", null=True, blank=True, verbose_name="Option", on_delete=models.SET_NULL)
    user_options = models.ManyToManyField(User, through='poll.UserOption')

    def get_percentage(self):
        all_user_options_count = 0
        for option in self.poll.option_set.all():
            for _ in option.useroption_set.all():
                all_user_options_count += 1

        if all_user_options_count == 0:
            return 0
        user_options_count = self.useroption_set.all().count()

        if user_options_count == 0:
            return 0

        if user_options_count:
            return int((user_options_count/all_user_options_count)*100)
        else:
            return int((user_options_count/all_user_options_count)*100)

    def get_participants_count(self):
        total = UserOption.objects.filter(option__poll=self.poll, selected=True).distinct().count()
        useroptions_count = 0
        for _ in self.useroption_set.filter(selected=True):
            useroptions_count += 1
        return f'{useroptions_count}/{total}'


class UserOption(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    option = models.ForeignKey("poll.Option", null=True, blank=True, on_delete=models.SET_NULL)
    selected = models.BooleanField(default=False)
    created_datetime = models.DateTimeField(null=True, auto_now=True)

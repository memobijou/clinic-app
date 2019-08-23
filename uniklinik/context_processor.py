from django.conf import settings  # import the settings file
from django.db.models import Count, Case, When
from taskmanagement.models import Task


def settings_context(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'settings': settings, "global_tasks": Task.objects.all().annotate(completed_count=Count(
        Case(When(usertasks__completed=True,then="usertasks")))).annotate(
        users_count=Count("users"),
    ).order_by("end_datetime").distinct()[:10]}

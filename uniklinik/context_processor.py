import json
import boto3
from django.conf import settings  # import the settings file
from django.db.models import Count, Case, When
from taskmanagement.models import Task
from botocore.exceptions import ClientError


def settings_context(request):
    if hasattr(settings, "AWS_ACCESS_KEY_ID"):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        key = "media/config/config.json"
        try:
            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
            f = response['Body']
            config = json.load(f)
        except ClientError as e:
            config = {}
    else:
        path = settings.MEDIA_ROOT + '/config/'
        try:
            with open(path + "config.json", "r") as f:
                config = json.load(f)
        except OSError as e:
            config = {}

    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'settings': settings, "global_tasks": Task.objects.all().annotate(completed_count=Count(
        Case(When(usertasks__completed=True,then="usertasks")))).annotate(
        users_count=Count("users"),
    ).order_by("end_datetime").distinct()[:10], "config": config}

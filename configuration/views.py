from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse_lazy
# Create your views here.
from configuration.forms import ConfigForm
import os
from django.forms.fields import ImageField
from django.core.exceptions import ValidationError
import boto3
from django.contrib.staticfiles import finders
import requests


def handle_uploaded_file(f, form):
    try:
        ImageField().to_python(f)
    except ValidationError as e:
        for error in e.error_list:
            form.add_error("logo", error.message)
        return

    if hasattr(settings, "AWS_ACCESS_KEY_ID"):
        handle_boto3_upload(f)
        return

    path = settings.MEDIA_ROOT + '/company/'
    file_path = path + "logo" + "." + f.name.split(".")[len(f.name.split("."))-1]

    if not os.path.exists(path):
        os.mkdir(path)

    for filename in os.listdir(path):
        if filename.startswith("logo"):
            os.remove(path + filename)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def handle_boto3_upload(f):
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    new_key = "media/company/logo" + "." + f.name.split(".")[len(f.name.split("."))-1]
    bucket.put_object(Key=new_key, Body=f)

    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='media/company/')

    if "Contents" not in response:
        return
    else:
        objs = response['Contents']
        to_delete_keys = []
        for obj in objs:
            if obj["Key"] != new_key:
                to_delete_keys.append({"Key": obj["Key"]})

        if len(to_delete_keys) > 0:
            s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            s3.meta.client.delete_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Delete={"Objects": to_delete_keys})


@login_required
def configuration_view(request):
    logo_url = reverse_lazy("config:logo")

    if request.POST:
        form = ConfigForm(data=request.POST, files=request.FILES)
        if form.is_valid() is True:
            handle_uploaded_file(request.FILES['logo'], form)
            if form.is_valid() is True:
                if hasattr(settings, "AWS_ACCESS_KEY_ID"):
                    mapper_url = os.environ.get("mapper_url") + "/api/v1/mandators/submission/"
                    host_url = os.environ.get("host_url")
                    requests.post(mapper_url, data={"url": host_url,
                                                    "logo_url": str(request.build_absolute_uri()) + logo_url})
                return HttpResponseRedirect(reverse_lazy("config:config"))
    else:
        form = ConfigForm()

    return render(request, 'configuration/configuration.html',
                  {"form": form, "logo_url": logo_url})


def logo_view(request):
    if hasattr(settings, "AWS_ACCESS_KEY_ID"):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='media/company/')

        if "Contents" not in response:
            with open(settings.STATIC_ROOT + "/ukgm_logo.jpg", "rb") as f:
                response = HttpResponse(f.read(), content_type='application/force-download')
                filename = f.name.split("/")[len(f.name.split("/")) - 1]
                response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
                return response

        objs = response['Contents']
        latest = max(objs, key=lambda x: x['LastModified'])
        key = latest["Key"]
        response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        f = response['Body']
        response = HttpResponse(f.read(), content_type='application/force-download')
        filename = key.split("/")[len(key.split("/"))-1]
        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
        return response
    else:
        path = settings.MEDIA_ROOT + '/company/'

        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.startswith("logo"):
                    with open(path + f"/{filename}", "rb") as f:
                        response = HttpResponse(f.read(), content_type='application/force-download')
                        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
                        return response

        path = finders.find('ukgm_logo.jpg')

        with open(path, "rb") as f:
            response = HttpResponse(f.read(), content_type='application/force-download')
            filename = f.name.split("/")[len(f.name.split("/")) - 1]
            response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
            return response

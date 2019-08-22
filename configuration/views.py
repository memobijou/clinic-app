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
from django.contrib.staticfiles.storage import staticfiles_storage
import boto3
import base64


def handle_uploaded_file(f, form):
    if settings.AWS_ACCESS_KEY_ID:
        handle_boto3_upload(f, form)
        return

    path = settings.MEDIA_ROOT + '/company/'
    file_path = path + "logo" + "." + f.name.split(".")[len(f.name.split("."))-1]

    if not os.path.exists(path):
        os.mkdir(path)

    try:
        ImageField().to_python(f)
    except ValidationError as e:
        for error in e.error_list:
            form.add_error("logo", error.message)
        return

    for filename in os.listdir(path):
        if filename.startswith("logo"):
            os.remove(path + filename)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def handle_boto3_upload(f, form):
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket.put_object(Key="media/company/logo" + "." + f.name.split(".")[len(f.name.split("."))-1], Body=f)


@login_required
def configuration_view(request):
    if request.POST:
        form = ConfigForm(data=request.POST, files=request.FILES)
        if form.is_valid() is True:
            handle_uploaded_file(request.FILES['logo'], form)
            if form.is_valid() is True:
                return HttpResponseRedirect(reverse_lazy("config:config"))
    else:
        form = ConfigForm()

    logo_encoded = None
    if settings.AWS_ACCESS_KEY_ID:
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='media/company/logo.jpg')
        f = response['Body']
        logo_encoded = base64.b64encode(f.read()).decode('ascii')

    return render(request, 'configuration/configuration.html',
                  {"form": form, "logo_url": staticfiles_storage.url("ukgm_logo.jpg"), "logo_encoded": logo_encoded})


def logo_view(request):
    if settings.AWS_ACCESS_KEY_ID:
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='media/company/')
        objs = response['Contents']
        latest = max(objs, key=lambda x: x['LastModified'])

        response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=latest["key"])
        f = response['Body']
        response = HttpResponse(f.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=\"request.txt\"'
        return response

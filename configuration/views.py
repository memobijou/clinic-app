from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse_lazy
# Create your views here.
from configuration.forms import ConfigForm
import os
from django.forms.fields import ImageField
from django.core.exceptions import ValidationError
from django.contrib.staticfiles.storage import staticfiles_storage


def handle_uploaded_file(f, form):
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

    return render(request, 'configuration/configuration.html',
                  {"form": form, "logo_url": staticfiles_storage.url("ukgm_logo.jpg")})

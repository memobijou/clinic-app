"""uniklinik URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from uniklinik.views import CustomAuthToken

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='main.html')), name="main"),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name="privacy"),
    path('admin/', admin.site.urls),
    path('account/', include(("account.urls", "account"), namespace="account")),
    path('appointment/', include(("appointment.urls", "appointment"), namespace="appointment")),
    path('filestorage/', include(("filestorage.urls", "filestorage"), namespace="filestorage")),
    path('taskmanagement/', include(("taskmanagement.urls", "taskmanagement"), namespace="taskmanagement")),
    path('accomplishment/', include(("accomplishment.urls", "accomplishment"), namespace="accomplishment")),
    path('messaging/', include(("messaging.urls", "messaging"), namespace="messaging")),
    path('phone-books/', include(("phonebook.urls", "phonebook"), namespace="phonebook")),
    path('config/', include(("configuration.urls", "configuration"), namespace="config")),
    path('subject-areas/', include(("subject_area.urls", "subject_area"), namespace="subject_area")),
    path('polls/', include(("poll.urls", "poll"), namespace="poll")),
    path(r'api-auth/', include('rest_framework.urls')),
    path('api/v1/', include(('accomplishment.api_urls', "accomplishment"), namespace="api_accomplishment")),
    path('api/v1/', include(('poll.api_urls', "poll"), namespace="api_poll")),
    path('api/v1/', include(('proposal.api_urls', "proposal"), namespace="api_proposal")),
    path('api/v1/', include(('account.api_urls', "account"), namespace="api_account")),
    path('api/v1/', include(('phonebook.api_urls', "phonebook"), namespace="api_phonebook")),
    path('api/v1/', include(('subject_area.api_urls', "subject_area"), namespace="api_subject_area")),
    path('api/v1/', include(('messaging.api_urls', "messaging"), namespace="api_messaging")),
    path('api/v1/', include(('taskmanagement.api_urls', "taskmanagement"), namespace="api_taskmanagement")),
    path('api/v1/', include(('appointment.api_urls', "appointment"), namespace="api_appointment")),
    path('api/v1/', include(('filestorage.api_urls', "filestorage"), namespace="api_filestorage")),
    path('api/v1/', include(('broadcast.api_urls', "broadcast"), namespace="api_broadcast")),
]

urlpatterns += [
    path(r'api-token-auth/', CustomAuthToken.as_view())
]

if settings.DEBUG is True:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

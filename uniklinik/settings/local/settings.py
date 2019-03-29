from uniklinik.settings.base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "postgres",
        'USER': "postgres",
        'PASSWORD': "postgres",
        'HOST': "db",
        'PORT': 5432,
    }
}


WEBPACK_DEV_SERVER = True

from uniklinik.settings.base import *
import dj_database_url

# CUSTOM
DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL
    )
}


# AWS - Credentials

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# AWS - Media

DEFAULT_FILE_STORAGE = 'uniklinik.settings.storage_backends.MediaStorage'  # <-- here is where we reference it

SECRET_KEY = os.environ.get("SECRET_KEY")

PREPEND_WWW = True
BASE_URL = "https://ukgm.cliniclink.de"
SECURE_SSL_REDIRECT = True

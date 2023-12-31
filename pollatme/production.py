"""
Django settings for pollatme project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from .base_settings import *
from os import environ, path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in environ else []

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": f"django.db.backends.postgresql",
        "NAME": environ.get('DB_NAME'),
        "USER": environ.get('DB_USER'),
        "PASSWORD": environ.get('DB_PASSWORD'),
        "HOST": environ.get('DB_HOST'),
        "PORT": environ.get('DB_PORT', '')
    }
}

STATIC_URL = environ.get("DJANGO_STATIC_URL", "/static/")
STATIC_ROOT = path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = ('whitenoise.storage.CompressedStaticFilesStorage')
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
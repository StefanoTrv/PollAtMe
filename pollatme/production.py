"""
Django settings for pollatme project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from os import environ, path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-tw(*s1_&$8oa)19y(fu)uyc^)yzs6h4^7fz*ny0ezbp@bker@d"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in environ else []

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "polls.apps.PollsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cookiebanner"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "polls.middleware.NewPollSessionCleaner",
]

ROOT_URLCONF = "pollatme.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pollatme.wsgi.application"


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


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = environ.get('TIME_ZONE', "UTC")

USE_I18N = True

USE_TZ = bool(environ.get('USE_TZ', True))


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = environ.get("DJANGO_STATIC_URL", "/static/")
STATIC_ROOT = path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = ('whitenoise.storage.CompressedStaticFilesStorage')


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

COOKIEBANNER = {
    "title": _("Cookie settings"),
    "header_text": _("We are using cookies on this website. A few are essential, others are not."),
    "footer_text": _("Please accept our cookies"),
    "footer_links": [
        {"title": _("Imprint"), "href": "/imprint"},
        {"title": _("Privacy"), "href": "/privacy"},
    ],
    "groups": [
        {
            "id": "essential",
            "name": _("Essential"),
            "description": _("Essential cookies allow this page to work."),
            "cookies": [
                {
                    "pattern": "cookiebanner",
                    "description": _("Meta cookie for the cookies that are set."),
                },
                {
                    "pattern": "csrftoken",
                    "description": _("This cookie prevents Cross-Site-Request-Forgery attacks."),
                },
                {
                    "pattern": "sessionid",
                    "description": _("This cookie is necessary to allow logging in, for example."),
                },
            ],
        },
        {
            "id": "analytics",
            "name": _("Analytics"),
            "optional": True,
            "cookies": [
                {
                    "pattern": "_pk_.*",
                    "description": _("Matomo cookie for website analysis."),
                },
            ],
        },
    ],
}
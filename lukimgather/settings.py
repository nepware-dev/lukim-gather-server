import importlib.util
import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from environs import Env
from marshmallow.validate import OneOf

# Read .env file for environment variable
env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Server environment
SERVER_ENVIRONMENT = env.str(
    "SERVER_ENVIRONMENT",
    validate=OneOf(choices=["development", "testing", "staging", "production"]),
    error="SERVER_ENVIRONMENT can only be one of {choices}",
)

# Is server secure server?
IS_SERVER_SECURE = SERVER_ENVIRONMENT in ["staging", "production"]

# Secret key for server
if IS_SERVER_SECURE:
    SECRET_KEY = env.str("DJANGO_SECRET_KEY", validate=lambda n: len(n) > 49)
else:
    SECRET_KEY = env.str(
        "DJANGO_SECRET_KEY",
        validate=lambda n: len(n) > 49,
        default=get_random_secret_key(),
    )

# Debug
if IS_SERVER_SECURE:
    DEBUG = False
else:
    DEBUG = True

# List of allowed hosts
DJANGO_ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[], subcast=str)
if IS_SERVER_SECURE:
    ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS
else:
    LOCAL_ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1"]
    ALLOWED_HOSTS = LOCAL_ALLOWED_HOSTS + DJANGO_ALLOWED_HOSTS


# Application definition

# Apps which need to be before django default apps
BEFORE_DJANGO_APPS = []

# Django apps
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

# Internal apps
INTERNAL_APPS = [
    "user",
]

# Third party apps
THIRD_PARTY_APPS = [
    "django_filters",
    "graphene_django",
]

INSTALLED_APPS = BEFORE_DJANGO_APPS + DJANGO_APPS + INTERNAL_APPS + THIRD_PARTY_APPS

# Add django extensions to installed app?
if importlib.util.find_spec("django_extensions"):
    INSTALLED_APPS.append("django_extensions")

# MIDDLEWARES
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Graphene
GRAPHENE = {
    "SCHEMA": "lukimgather.schema.schema",
    "SCHEMA_INDENT": 2,
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

if DEBUG:
    GRAPHENE["MIDDLEWARE"] += [
        "graphene_django.debug.DjangoDebugMiddleware",
    ]


# Authentication Backends
AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "lukimgather.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

WSGI_APPLICATION = "lukimgather.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Database
DATABASES = {
    "default": env.dj_db_url("DATABASE_URL", default="spatialite:///db.sqlite3")
}

# CACHES
CACHE = {"default": env.dj_cache_url("CACHE_URL", default="dummy://")}

# AUTH User model
AUTH_USER_MODEL = "user.User"

# Password validation
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

# Email
email_config = env.dj_email_url(
    "EMAIL_URL",
    default="console://user:password@localhost?_server_email=root@localhost&_default_from_email=root@localhost",
)
EMAIL_FILE_PATH = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL = email_config["EMAIL_USE_SSL"]
if "SERVER_EMAIL" in email_config:
    SERVER_EMAIL = email_config["SERVER_EMAIL"]
if "DEFAULT_FROM_EMAIL" in email_config:
    DEFAULT_FROM_EMAIL = email_config["DEFAULT_FROM_EMAIL"]

# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# CELERY
ENABLE_CELERY = env.bool("ENABLE_CELERY", default=True)

if ENABLE_CELERY:
    CELERY_BROKER_TYPE = env.str(
        "CELERY_BROKER_TYPE",
        default="filesystem",
        validate=OneOf(choices=["redis", "filesystem"]),
        error="CELERY_BROKER_TYPE can only be one of {choices}",
    )

    if CELERY_BROKER_TYPE == "redis":
        CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
        CELERY_RESULT_BACKEND = CELERY_BROKER_URL
        if CELERY_BROKER_URL.startswith("rediss://"):
            CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": "CERT_OPTIONAL"}

    if CELERY_BROKER_TYPE == "filesystem":
        CELERY_BROKER_URL = "filesystem://"
        CELERY_RESULT_BACKEND = "file:///tmp"
        CELERY_BROKER_TRANSPORT_OPTIONS = {
            "data_folder_in": "/tmp",
            "data_folder_out": "/tmp",
            "data_folder_processed": "/tmp",
        }

    CELERY_TIMEZONE = TIME_ZONE
    CELERY_WORKER_HIJACK_ROOT_LOGGER = False
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

import importlib.util
import os
from datetime import timedelta
from pathlib import Path

import boto3
import django.conf.locale
import sentry_sdk
from django.conf import global_settings
from django.core.management.utils import get_random_secret_key
from django.utils.translation import gettext_lazy as _
from environs import Env
from marshmallow.validate import OneOf
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

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
BEFORE_DJANGO_APPS = [
    "modeltranslation",
    "admin_interface",
    "colorfield",
]

# Django apps
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.sites",
]

# Internal apps
INTERNAL_APPS = [
    "discussion",
    "gallery",
    "notification",
    "organization",
    "project",
    "region",
    "survey",
    "support",
    "user",
]

# Third party apps
THIRD_PARTY_APPS = [
    "admin_auto_filters",
    "corsheaders",
    "ckeditor",
    "ckeditor_uploader",
    "django_filters",
    "django_json_widget",
    "graphene_django",
    "graphql_jwt.refresh_token.apps.RefreshTokenConfig",
    "mptt",
    "ordered_model",
    "phonenumber_field",
    "rest_framework",
    "rest_framework_gis",
    "reversion",
    "oauth2_provider",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

INSTALLED_APPS = BEFORE_DJANGO_APPS + DJANGO_APPS + INTERNAL_APPS + THIRD_PARTY_APPS

# Add django extensions to installed app?
if importlib.util.find_spec("django_extensions"):
    INSTALLED_APPS.append("django_extensions")

# X frame options
X_FRAME_OPTIONS = "SAMEORIGIN"

# MIDDLEWARES
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

GRAPHENE_DJANGO_EXTRAS = {
    "DEFAULT_PAGINATION_CLASS": "graphene_django_extras.paginations.LimitOffsetGraphqlPagination",
    "DEFAULT_PAGE_SIZE": 100,
    "MAX_PAGE_SIZE": 200,
    "CACHE_ACTIVE": True,
    "CACHE_TIMEOUT": 300,
}

GRAPHQL_JWT = {
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_VERIFY_EXPIRATION": False,
    "JWT_EXPIRATION_DELTA": timedelta(days=30),
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(weeks=27),
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_ALGORITHM": "HS512",
}

if DEBUG:
    GRAPHENE["MIDDLEWARE"] += [
        "graphene_django.debug.DjangoDebugMiddleware",
    ]

# CORS settings
CORS_URLS_REGEX = r"^/(graphql|protected_area_tiles).*$"
CORS_ALLOWED_ORIGIN_REGEXES = env.list(
    "CORS_ALLOWED_ORIGIN_REGEXES", default=[], subcast=str
)


# Authentication Backends
AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
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

# Amazon Simple Notification Service (SNS)
ENABLE_SNS = env.bool("ENABLE_SNS", default=False)
if ENABLE_SNS:
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
    AWS_SNS_REGION_NAME = env.str("AWS_SNS_REGION_NAME")

# Internationalization

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

gettext = lambda s: s

LANGUAGES = (
    ("en", _("English")),
    ("ho", _("Hiri Motu")),
    ("tpi", _("Tok Pisin")),
)

EXTRA_LANG_INFO = {
    "ho": {
        "bidi": False,
        "code": "ho",
        "name": "Hiri Motu",
        "name_local": "Hiri Motu",
    },
    "tpi": {
        "bidi": False,
        "code": "tpi",
        "name": "Tok Pisin",
        "name_local": "Tok Pisin",
    },
}

# Add extra languages
django.conf.locale.LANG_INFO = dict(django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO)
global_settings.LANGUAGES = global_settings.LANGUAGES + [
    ("ho", "Hiri Motu"),
    ("tpi", "Tok Pisin"),
]

# Model translation
MODELTRANSLATION_PREPOPULATE_LANGUAGE = "en"
MODELTRANSLATION_AUTO_POPULATE = True

# Cloudwatch based logging
ENABLE_WATCHTOWER = env.bool("ENABLE_WATCHTOWER", default=False)

if ENABLE_WATCHTOWER:
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")

    AWS_CLOUDWATCH_REGION_NAME = env.str("AWS_CLOUDWATCH_REGION_NAME")
    AWS_LOG_GROUP_NAME = env.str("AWS_LOG_GROUP_NAME")

    logger_boto3_client = boto3.client(
        "logs",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_CLOUDWATCH_REGION_NAME,
    )

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": "DEBUG",
            "handlers": ["watchtower", "console"],
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            "watchtower": {
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_client": logger_boto3_client,
                "log_group_name": AWS_LOG_GROUP_NAME,
                "level": "INFO",
            },
        },
        "loggers": {
            "django": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": IS_SERVER_SECURE,
            }
        },
    }


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

# CKEDITOR settings
CKEDITOR_UPLOAD_PATH = "ckeditor-uploads/"

# Sentry
ENABLE_SENTRY = env.bool("ENABLE_SENTRY", default=False)
if ENABLE_SENTRY:
    sentry_sdk.init(
        dsn=env.url("SENTRY_DSN"),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment=SERVER_ENVIRONMENT,
    )

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SITE_ID = 1
LOGIN_URL = "/accounts/login/"

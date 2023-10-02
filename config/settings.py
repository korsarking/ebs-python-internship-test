"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import dj_email_url
from environs import Env
from datetime import timedelta
from pathlib import Path

from django.utils.translation import gettext_lazy as _

env = Env(eager=False)
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_yasg",
    # Local apps
    "apps.common",
    "apps.users",
    "apps.tasks"
]

MIDDLEWARE = [
    # Default Django middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Third party middleware
    "corsheaders.middleware.CorsMiddleware",
    # Local middleware
    "apps.common.middlewares.ApiMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "token",
    "cache-control",
)

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_FILTER_BACKENDS': ["django_filters.rest_framework.DjangoFilterBackend",
                                "rest_framework.filters.SearchFilter",
                                "rest_framework.filters.OrderingFilter"],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12
}


SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=500),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
FIXTURE_DIRS = ("fixtures/",)

DEFAULT_LANG = "ro"
LANGUAGES = [
    (DEFAULT_LANG, _("Romanian")),
    ("ru", _("Russian")),
    ("en", _("English")),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "users.user"

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

email = env.dj_email_url("EMAIL_URL", default="smtp://")
EMAIL_HOST = email["EMAIL_HOST"]
EMAIL_PORT = email["EMAIL_PORT"]
EMAIL_HOST_PASSWORD = email["EMAIL_HOST_PASSWORD"]
EMAIL_HOST_USER = email["EMAIL_HOST_USER"]
EMAIL_USE_TLS = email["EMAIL_USE_TLS"]
EMAIL_BACKEND = email["EMAIL_BACKEND"]
DEFAULT_FROM_EMAIL = email.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

DATE_FORMAT = "%Y-%m-%d %H:%m"

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

CACHE_TTL = 60

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WSGI_AUTO_RELOAD = True

DEBUG_LEVEL = "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s]- %(message)s"}},
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "handlers": {
        "console": {
            "level": DEBUG_LEVEL,
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "standard",
        }
    },
    "loggers": {
        "info": {"handlers": ["console"], "level": DEBUG_LEVEL, "propagate": True},
        "django": {
            "handlers": ["console"],
            "level": DEBUG_LEVEL,
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": DEBUG_LEVEL,
            "propagate": True,
        },
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    },
}

# LOGGING = {
#     "version": 1,
#     "filters": {
#         "require_debug_true": {
#             "()": "django.utils.log.RequireDebugTrue",
#         }
#     },
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "filters": ["require_debug_true"],
#             "class": "logging.StreamHandler",
#         }
#     },
#     "loggers": {
#         "django.db.backends": {
#             "level": "DEBUG",
#             "handlers": ["console"],
#         }
#     },
# }

env.seal()

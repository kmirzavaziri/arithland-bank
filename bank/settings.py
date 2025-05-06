import os
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import schedule
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-8zas42xgit5l1ok21wz1gmf8r4wy666999gotu5fuc5ehc42k0")

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# TODO
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "bank",
    "transaction",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "transaction.middlewares.TimezoneMiddleware",
]

ROOT_URLCONF = "bank.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bank.template.add_base_context",
            ],
        },
    },
]

WSGI_APPLICATION = "bank.wsgi.application"

if db_host := os.getenv("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASS"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SCHEDULER_CONFIG = {
    "jobs": {
        "my_task": {
            "function": "transactions.tasks.add_interests",
            "args": [],
            "kwargs": {},
            "trigger": schedule.every(10).seconds,
        },
    }
}

AUTH_USER_MODEL = "transaction.User"

ADMIN_SITE_HEADER = "Arithland Bank"
ADMIN_SITE_TITLE = "Arithland Bank"
ADMIN_INDEX_TITLE = "Admin"


@dataclass
class MenuItem:
    name: str
    url: str
    icon: Optional[str] = None


MENU_COMMON = [
    MenuItem("Dashboard", reverse_lazy("dashboard"), "fas fa-home"),
    MenuItem("Teams", reverse_lazy("teams"), "fas fa-link"),
]

MENU_ADMIN = [
    *MENU_COMMON,
    MenuItem("Transactions", reverse_lazy("transactions")),
    MenuItem("Admin", reverse_lazy("admin:index")),
]

JAZZMIN_SETTINGS = {
    "site_logo": "assets/img/logo.png",
    "topmenu_links": [asdict(item) for item in MENU_ADMIN],
    "show_sidebar": False,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "transaction": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

CSRF_TRUSTED_ORIGINS = [
    "https://bank.arith.land",
    "http://127.0.0.1",
    "http://localhost",
]

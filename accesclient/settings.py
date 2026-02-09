"""
Django settings for accesclient project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------
# Base directory
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# Security
# ------------------------------
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

CSRF_TRUSTED_ORIGINS = [
    'http://webclient.astus.fr:8090',
    'https://webclient.astus.fr:8090', 
    'http://webacces.astus.fr',
    'https://webacces.astus.fr',
    'http://acces-client.onrender.com:8090',
    'https://acces-client.onrender.com:8090',
    'http://acces-client.onrender.com',
    'https://acces-client.onrender.com',
]

# ------------------------------
# Applications
# ------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accesclient",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # for serving static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "accesclient.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "accesclient" / "templates"],
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

WSGI_APPLICATION = "accesclient.wsgi.application"

# ------------------------------
# Databases
# ------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv('DB_DEFAULT_NAME'),
        "USER": os.getenv('DB_DEFAULT_USER'),
        "PASSWORD": os.getenv('DB_DEFAULT_PASSWORD'),
        "HOST": os.getenv('DB_DEFAULT_HOST'),
        "PORT": os.getenv('DB_DEFAULT_PORT'),
    },
    "astreinte_db": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv('DB_ASTREINTE_NAME'),
        "USER": os.getenv('DB_ASTREINTE_USER'),
        "PASSWORD": os.getenv('DB_ASTREINTE_PASSWORD'),
        "HOST": os.getenv('DB_ASTREINTE_HOST'),
        "PORT": os.getenv('DB_ASTREINTE_PORT'),
    },
}

DATABASE_ROUTERS = ["accesclient.db_router.DatabaseRouter"]

# ------------------------------
# Password validation
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------
# Internationalization
# ------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# ------------------------------
# Static files
# ------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "accesclient" / "static",  # optional: where you keep static files during development
]

# Use WhiteNoise for production static serving
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------
# Default primary key field type
# ------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------
# Email configuration via Microsoft Graph API
# ------------------------------
EMAIL_BACKEND = "accesclient.email_backend.MicrosoftGraphEmailBackend"
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
DEFAULT_FROM_EMAIL = "astus@astus.fr"

# ------------------------------
# Authentication
# ------------------------------
LOGIN_REDIRECT_URL = "/messages_ascenseurs/"
LOGOUT_REDIRECT_URL = "login"

AUTHENTICATION_BACKENDS = [
    "accesclient.backends.LastNameAuthBackend",
]

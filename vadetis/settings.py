"""
Django settings for vadetis project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u)0a*o(9z(*wcrj8$wq421r0g&4xd0@e&2)2kzum5p2=9@=_z9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

#MAX POST SIZE INCREASED FOR LARGE DATASETS
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600 #100MB

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # required for django-allauth
    'django_extensions', # needed for jupyter notebooks
    'vadetisweb',
    'django_celery_results',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework_datatables',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vadetis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'), # global templates, e.g. admin backend
            os.path.join(BASE_DIR, 'vadetisweb', 'templates'), # vadetisweb site templates
            os.path.join(BASE_DIR, 'vadetisweb', 'templates', 'allauth') # vadetisweb allauth templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.request', # required for django-allauth
            ],
        },
    },
]

WSGI_APPLICATION = 'vadetis.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vadetisv2',
        'USER': 'vadetisadmin',
        'PASSWORD': 'Cast40analysts5Roofing',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of django-allauth
    'django.contrib.auth.backends.ModelBackend',

    # django-allauth specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    # Use Django's standard 'django.contrib.auth' permissions,
    # or allow read-only access for unauthenticated users.

    'DEFAULT_AUTHENTICATION_CLASSES' : (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_PERMISSION_CLASSES' : (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

# Login - Config
LOGIN_REDIRECT_URL = 'vadetisweb:index'
ACCOUNT_LOGOUT_REDIRECT_URL = 'vadetisweb:index'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
ACCOUNT_USERNAME_VALIDATORS = 'vadetisweb.validators.username_validators'

ACCOUNT_FORMS = {
    'login' : 'vadetisweb.forms.AccountLoginForm',
    'signup' : 'vadetisweb.forms.AccountSignUpForm',
    'reset_password' : 'vadetisweb.forms.AccountResetPasswordForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    'change_password': 'vadetisweb.forms.AccountChangePasswordForm',
    'set_password': 'vadetisweb.forms.AccountSetPasswordForm',
    'disconnect': 'vadetisweb.forms.AccountSocialDisconnectForm',
}

SOCIALACCOUNT_FORMS = {
    'login': 'allauth.socialaccount.forms.DisconnectForm',
    'signup': 'vadetisweb.forms.SocialAccountSignupForm',
}

SOCIALACCOUNT_PROVIDERS = {
     'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# MAILING - CHANGE MAIL SETTINGS WHEN GOING PRODUCTION!
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'lisaexascale@gmail.com'
EMAIL_HOST_PASSWORD = 'svQcdxXQ'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# CELERY CONFIG
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_RESULT_EXPIRES = timedelta(days=30)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Europe/Zurich'

# BREADCRUMBS
BREADCRUMBS_TEMPLATE = 'vadetisweb/parts/breadcrumbs.html'

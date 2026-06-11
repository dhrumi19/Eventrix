"""
Django settings for eventrix project.
"""

from pathlib import Path
import os
import environ

# Compatibility Patch for Django 4.2 on Python 3.14.x
# The template rendering engine copies Context objects which fails on Python 3.14 due to changes in super() copy methods.
from django.template.context import Context
def patched_context_copy(self):
    duplicate = Context(self)
    duplicate.dicts = self.dicts[:]
    return duplicate
Context.__copy__ = patched_context_copy

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    RAZORPAY_KEY_ID=(str, ""),
    RAZORPAY_KEY_SECRET=(str, ""),
    USE_RAZORPAY_SIMULATION=(bool, True),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-hplqb5(d#@e*yoq!#&@*(rq76=)wgi15qs#0+4d@6jr$rlatl-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom apps
    'accounts',
    'events',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eventrix.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eventrix.wsgi.application'


# Database
# Use PostgreSQL if DATABASE_URL is configured, else fallback to SQLite
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Password validation
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


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication redirects
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dhrumishah74@gmail.com'
EMAIL_HOST_PASSWORD = 'jjxk yimy kzhy znnt'
EMAIL_USE_TLS = True
EMAIL_PORT = 587 

# Razorpay settings
RAZOR_KEY_ID = 'rzp_test_SP40oDmbLe1gev'
RAZOR_KEY_SECRET = 'hAQNJcjE91hR1Sx9I60in9hP'
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default=RAZOR_KEY_ID)
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default=RAZOR_KEY_SECRET)
USE_RAZORPAY_SIMULATION = env('USE_RAZORPAY_SIMULATION')

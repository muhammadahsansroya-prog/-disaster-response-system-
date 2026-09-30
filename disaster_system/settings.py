"""
Django settings for disaster_system project.
"""

from pathlib import Path
import pymysql

# PyMySQL ko MySQLdb ki tarah register karein (XAMPP compatibility ke liye)
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-qr44t346x7ey1(bma^d=zcx)8)mgwqyuh23fnxib_o124jw5uw'

DEBUG = True

ALLOWED_HOSTS = ['ahsan32638.pythonanywhere.com', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'disaster_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'disaster_system.wsgi.application'


# XAMPP MySQL Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'disaster_db',       # XAMPP phpMyAdmin mein jo Database banaya hai
        'USER': 'root',              # XAMPP MySQL default user
        'PASSWORD': '',              # XAMPP MySQL default password khali hota hai
        'HOST': '127.0.0.1',         # Localhost IP
        'PORT': '3306',              # Default MySQL Port
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Authentication Redirects
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/responder/'
LOGOUT_REDIRECT_URL = '/login/'

# Security & HTTPS Configuration
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SILENCED_SYSTEM_CHECKS = ['models.E015']
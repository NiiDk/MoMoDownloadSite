# InsightInnovations/settings.py

from pathlib import Path
from decouple import config 
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ====================================================================
# SECURITY AND HOSTS
# ====================================================================

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Parse ALLOWED_HOSTS from config
allowed_hosts_str = config('ALLOWED_HOSTS', default='127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

# Add additional hosts
additional_hosts = [
    config('NGROK_TUNNEL', default='').replace('https://', '').replace('http://', '').split('/')[0],
    '.render.com',
    'InsightInnovations.onrender.com',
    config('RENDER_EXTERNAL_HOSTNAME', default=''),
]

for host in additional_hosts:
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# ====================================================================
# CLOUDINARY CONFIGURATION (MUST BE BEFORE OTHER SETTINGS)
# ====================================================================

# Configure Cloudinary from CLOUDINARY_URL
cloudinary.config(secure=True)

# ====================================================================
# API KEYS
# ====================================================================

PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')
ARKESEL_API_KEY = config('ARKESEL_API_KEY')
CURRENCY_CODE = config('CURRENCY_CODE', default='GHS')

# ====================================================================
# EMAIL CONFIG
# ====================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# ====================================================================
# APPLICATIONS
# ====================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # Custom app
    'shop',
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

ROOT_URLCONF = 'InsightInnovations.urls'

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
                'shop.context_processors.current_year',
            ],
        },
    },
]

WSGI_APPLICATION = 'InsightInnovations.wsgi.application'

# ====================================================================
# DATABASE
# ====================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ====================================================================
# PASSWORD VALIDATION
# ====================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ====================================================================
# INTERNATIONALIZATION
# ====================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ====================================================================
# STATIC & MEDIA FILES
# ====================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Add this if you have a static folder

# -----------------------------
# 🔥 STORAGE CONFIGURATION
# -----------------------------

# Django 4.2+ way (recommended)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Legacy way (compatible with older Django)
# MEDIA_URL = '/media/'
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Optional Cloudinary settings
CLOUDINARY_STORAGE = {
    # This helps avoid overwriting files with same name
    'overwrite': False,
    # You can specify a default folder for uploads
    # 'default_folder': 'InsightInnovations/media',
    # Resource type settings
    'resource_type': 'auto',
    # Validation
    'validate_filename': True,
}

# ====================================================================
# DEFAULT PK
# ====================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====================================================================
# SECURITY SETTINGS (FOR PRODUCTION)
# ====================================================================

if not DEBUG:
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
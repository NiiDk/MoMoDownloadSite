# DarkSonSolutions/settings.py

"""
Django settings for DarkSonSolutions project.
"""

from pathlib import Path
# No change needed here if 'python-decouple' is in requirements.txt:
from decouple import config 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================================================================
# 🔒 SECURITY AND HOSTS (Load all secrets from .env)
# ====================================================================

# SECURITY WARNING: Loaded from .env file for security.
SECRET_KEY = config('SECRET_KEY') 

# SECURITY WARNING: Do NOT deploy with DEBUG = True!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    config('NGROK_TUNNEL', default=''), 
    '.render.com', 
    'momodownloadsite.onrender.com', # <--- YOUR ACTUAL LIVE DOMAIN
    config('RENDER_EXTERNAL_HOSTNAME', default=''),
]

# ====================================================================
# 🔑 CUSTOM SETTINGS: API KEYS AND CURRENCY (Loaded from .env)
# ====================================================================

# Paystack Keys (Loaded from .env file)
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')

# SMS (Arkesel) Key (Loaded from .env file)
ARKESEL_API_KEY = config('ARKESEL_API_KEY')

# Currency Setting
CURRENCY_CODE = 'GHS' 

# ====================================================================
# APPLICATION DEFINITION
# ====================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your custom application
    'shop', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 🔥 FIX 1: ADD WHITE NOISE HERE to serve static files in production (fixes Admin CSS)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DarkSonSolutions.urls'

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

WSGI_APPLICATION = 'DarkSonSolutions.wsgi.application'

# ====================================================================
# 💾 DATABASE
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

# ====================================================================
# 🖥️ STATIC FILES (CRITICAL FOR DEPLOYMENT)
# ====================================================================

# Base URL for static assets
STATIC_URL = 'static/'

# Directory where static files will be collected by 'collectstatic'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 🔥 FIX 2: TELL WHITENOISE HOW TO HANDLE STATIC FILES IN PRODUCTION
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
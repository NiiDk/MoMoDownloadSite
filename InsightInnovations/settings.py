# InsightInnovations/settings.py

"""
Django settings for InsightInnovations project.
"""

from pathlib import Path
from decouple import config # Ensures secure loading from .env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================================================================
# 🔒 1. SECURITY AND HOSTS (Loaded from .env)
# ====================================================================

SECRET_KEY = config('SECRET_KEY') 

# SECURITY WARNING: Do NOT deploy with DEBUG = True!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    config('NGROK_TUNNEL', default=''), 
    '.render.com', 
    'InsightInnovations.onrender.com', # <--- YOUR ACTUAL LIVE DOMAIN
    config('RENDER_EXTERNAL_HOSTNAME', default=''),
]

# ====================================================================
# 🔑 2. CUSTOM API KEYS AND CURRENCY (Loaded from .env)
# ====================================================================

# Paystack Keys (Loaded from .env file)
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')

# SMS (Arkesel) Key (Loaded from .env file)
ARKESEL_API_KEY = config('ARKESEL_API_KEY')

# Currency Setting
CURRENCY_CODE = 'GHS' 

# ====================================================================
# 📧 3. EMAIL CONFIGURATION (CRITICAL FOR CONTACT FORM)
# ====================================================================

# 1. Use SMTP backend (Gmail requires this)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 2. Connection Details (Pulled directly from .env)
EMAIL_HOST = config('EMAIL_HOST')                  # e.g., smtp.gmail.com
EMAIL_PORT = config('EMAIL_PORT', cast=int)       # e.g., 587
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool) # e.g., True

# 3. Credentials (Pulled from .env where App Password is set)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')        # e.g., darkosammy2@gmail.com
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD') # Your 16-character App Password

# 4. Set the default sender
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER') 

# ====================================================================
# 4. APPLICATION DEFINITION
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
    'whitenoise.middleware.WhiteNoiseMiddleware', # For serving static files in production
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
            ],
        },
    },
]

WSGI_APPLICATION = 'InsightInnovations.wsgi.application'

# ====================================================================
# 5. DATABASE
# ====================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', 
    }
}

# ====================================================================
# 6. PASSWORD VALIDATION
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
# 7. STATIC FILES (CRITICAL FOR DEPLOYMENT)
# ====================================================================

# Base URL for static assets
STATIC_URL = 'static/'

# Directory where static files will be collected by 'collectstatic'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
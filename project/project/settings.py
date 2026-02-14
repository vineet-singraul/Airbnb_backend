from pathlib import Path
from decouple import config
import os
import razorpay

BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================
# SECURITY SETTINGS
# ==============================

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')





import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Required for admin
        'DIRS': [BASE_DIR / "templates"],  # Optional: your custom templates folder
        'APP_DIRS': True,  # Look for templates inside apps automatically
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







# ==============================
# APPLICATIONS
# ==============================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'rest_framework',
    'corsheaders',

    # Local Apps
    'app',
]


# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==============================
# CORS
# ==============================

CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL', default=True, cast=bool)


# ==============================
# URLS & WSGI
# ==============================

ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'


# ==============================
# DATABASE (PostgreSQL)
# ==============================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# ==============================
# PASSWORD VALIDATION
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================
# INTERNATIONALIZATION
# ==============================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==============================
# STATIC & MEDIA FILES
# ==============================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================
# PAYMENT GATEWAYS
# ==============================

# Razorpay
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Stripe
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')








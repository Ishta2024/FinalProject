"""
Django settings for SleekMart project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CRISPY_TEMPLATE_PACK = 'bootstrap4'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5u%kjybv=%sm@+i%&oljv_y%&_7=*a=z*jmr6^#@94(br=r)r@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [

    'dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'widget_tweaks',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google'
    # 'social_django'
    
]
SITE_ID = 1
SOCIALACCOUNT_LOGIN_ON_GET=True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'SleekMart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'social_django.context_processors.backends'
            ],
        },
    },
]

WSGI_APPLICATION = 'SleekMart.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'dashboard.CustomUser'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# PASSWORD_RESET_CONFIRM_URL = 'password_reset_confirm'
# PASSWORD_RESET_EMAIL_TEMPLATE = 'path/to/password_reset_email.html'
 # 'social_core.backends.google.GoogleOAuth2',

AUTHENTICATION_BACKENDS = (
    
    'django.contrib.auth.backends.ModelBackend',
    # 'dashboard.custom_auth_backend.CustomAuthBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    # ...

    # ...
)


SOCIALACCOUNT_PROVIDERS ={
    'google':{
        'SCOPE' : [
            'profile',
            'email'
        ],
        'AUTH_PARAMS':{
            'access_type':'online'
        }
    }
}
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'

  # Replace 'your_app' with the actual name of your app

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mailtoshowvalidationok@gmail.com'
EMAIL_HOST_PASSWORD = 'qtwpnirvgsxzhtdo'
DEFAULT_FROM_EMAIL = 'mailtoshowvalidationok@gmail.com'
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'ishtarachelmathew2024@mca.ajce.in'  # Your Gmail address
# EMAIL_HOST_PASSWORD = 'IshtaRMM@123'  # Your Gmail password or an app password

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='398659767902-n5a7pknl9ed3bc70331hlf9bs143lpgl.apps.googleusercontent.com'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='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'

LOGIN_REDIRECT_URL = 'dashboard_home'
lOGOUT_REDIRECT_URL = '/'

LOGIN_URL = 'login_page'

SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
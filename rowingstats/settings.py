#Django settings for rowingstats project.

import os, dj_database_url

# if running locally, read .env file for env variables
if os.environ.get("RSPLATFORM") != "heroku":
    from dotenv import load_dotenv
    load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Security settings - use explicit string comparison for clarity and correctness
# Set env var to "false" or "0" to disable, anything else (or unset) enables the secure default
DEBUG = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")  # defaults to FALSE
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() not in ("false", "0", "no")  # defaults to TRUE
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "true").lower() not in ("false", "0", "no")  # defaults to TRUE
CSRF_COOKIE_HTTPONLY = os.getenv("CSRF_COOKIE_HTTPONLY", "true").lower() not in ("false", "0", "no")  # defaults to TRUE
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [
    'localhost',
    '.herokuapp.com',
    '.rowingstats.com',
]
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # Deprecated but kept for older browsers
X_FRAME_OPTIONS = 'DENY'

# Additional security headers for production
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Heroku and Cloudflare terminate SSL at the proxy level and forward requests
# over HTTP. This tells Django to trust the X-Forwarded-Proto header to
# determine if the original request was HTTPS, preventing infinite redirect loops.
# Both Heroku and Cloudflare set this header, so we enable it in production.
if not DEBUG:
    SECURE_PROXY_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'ajax_select',
    'crispy_forms',
    'crispy_bootstrap5',
    'rowing.apps.RowingConfig',
    'blog.apps.BlogConfig',
    'hrr.apps.HrrConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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

ROOT_URLCONF = 'rowingstats.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
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

# crispy forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

WSGI_APPLICATION = 'rowingstats.wsgi.application'
if DEBUG == True:
    from django.contrib.messages import constants as message_constants
    MESSAGE_LEVEL = message_constants.DEBUG

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# override the sqlite default with DATABASE_URL env variable
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
# USE_L10N removed in Django 4.0 (localization is now always enabled)
USE_TZ = True
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}
STATIC_URL = '/static/'
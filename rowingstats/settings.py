#Django settings for rowingstats project.

import os, dj_database_url

# if running locally, read .env file for env variables
if os.environ.get("RSPLATFORM") != "heroku":
	from dotenv import load_dotenv
	load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Security settings - bool statements assume false if env var not specified
DEBUG = bool(os.getenv("DEBUG")) # defaults to FALSE
SESSION_COOKIE_SECURE = not(bool(os.getenv("SESSION_COOKIE_SECURE"))) # defaults to TRUE
CSRF_COOKIE_SECURE = not(bool(os.getenv("CSRF_COOKIE_SECURE"))) # defaults to TRUE
CSRF_COOKIE_HTTPONLY = not(bool(os.getenv("CSRF_COOKIE_HTTPONLY"))) # defaults to TRUE
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [
	'localhost',
	'.herokuapp.com',
	'.rowingstats.com',
]
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Application definition
INSTALLED_APPS = [
	'ajax_select',
    'coverage',
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

WSGI_APPLICATION = 'rowingstats.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
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
USE_L10N = True
USE_TZ = True
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
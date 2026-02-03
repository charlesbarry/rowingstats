"""
Test settings for rowingstats.

Uses SQLite for local testing without requiring PostgreSQL.
"""
from .settings import *

# Force SQLite for tests - override any DATABASE_URL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database for speed
    }
}

# Disable DEBUG for test consistency
DEBUG = False

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable secure cookies for testing
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Skip HTTPS redirect in tests
SECURE_SSL_REDIRECT = False

# Use simple static file storage for tests (no manifest required)
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

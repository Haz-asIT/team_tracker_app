import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from decouple import config


# Email setup
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- OPTIONAL .env loading ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- OPTIONAL DATABASE_URL helper ---
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# --- OPTIONAL decouple config ---
try:
    from decouple import config
except ImportError:
    # fallback if python-decouple not installed
    def config(key, default=None, cast=str):
        val = os.getenv(key, default)
        if cast and val is not None:
            try:
                return cast(val)
            except Exception:
                return val
        return val

# EMAIL SETTINGS FOR DEVELOPMENT
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

# SECURITY SETTINGS
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"


# ALLOWED HOSTS (split comma-separated string into a list)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1").split(",")


# Ensure CSRF_TRUSTED_ORIGINS is properly formatted
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "https://127.0.0.1").split(",")


SESSION_COOKIE_HTTPONLY = True          # Prevent JavaScript access to session cookie
SESSION_COOKIE_SECURE = not DEBUG       # Send session cookie only over HTTPS (production)
SESSION_COOKIE_SAMESITE = "Lax"         # Reduce CSRF risk via browser cookie policy

CSRF_COOKIE_HTTPONLY = True             # Prevent JavaScript access to CSRF cookie (optional)
CSRF_COOKIE_SECURE = not DEBUG          # Send CSRF cookie only over HTTPS (production)
CSRF_COOKIE_SAMESITE = "Lax"            # Standard CSRF cookie protection

# Session timeout (idle)
SESSION_COOKIE_AGE = 30 * 60
SESSION_SAVE_EVERY_REQUEST = True # Reset session timer on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Logout when window closes

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "django_filters",
    "simple_history",
    # Custom apps
    "dashboard",
    "security.apps.SecurityConfig",
    "people_management",
    "task_management",
    'widget_tweaks',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "team_tracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom
                "people_management.context_processors.inject_person",
            ],
        },
    },
]

# Messages settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

WSGI_APPLICATION = "team_tracker.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# only override if DATABASE_URL is present + dj_database_url exists
if dj_database_url and os.getenv("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(default=os.getenv("DATABASE_URL"))

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
    "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "security.validators.SpecialCharacterValidator"},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]


# Internationalization
LANGUAGE_CODE = "en-ms"
TIME_ZONE = "Asia/Kuala_Lumpur"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Ensure STATICFILES_DIRS is empty in production (DEBUG=False)
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]
else:
    STATICFILES_DIRS = []

# Use Whitenoise to serve static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/security/login/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "staticfiles_debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.contrib.staticfiles": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

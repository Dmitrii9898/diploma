"""Настройки веб-сервиса «Договор.Онлайн».

Система учёта и сопровождения договоров на платные образовательные услуги
ЧОУ ВО «Московский университет им. С.Ю. Витте».
Автор: Курбатов Дмитрий Евгеньевич.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-educontract-kurbatov-change-me-000000000000000000",
)
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
_public_url = env("PUBLIC_URL", default="") or env("RENDER_EXTERNAL_URL", default="")
if _public_url and _public_url not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, _public_url]

SITE_NAME = "Договор.Онлайн"
SITE_CODE = "EduContract"
AUTHOR_NAME = "Курбатов Дмитрий Евгеньевич"
AUTHOR_ID = "70199902"
VKR_TOPIC = (
    "Разработка веб-сервиса учёта и сопровождения договоров "
    "на платные образовательные услуги университета"
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "contracts",
    "pages",
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
    "contracts.middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "config.urls"
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
                "contracts.context_processors.site_meta",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.AppUser"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:cabinet"
LOGOUT_REDIRECT_URL = "pages:home"

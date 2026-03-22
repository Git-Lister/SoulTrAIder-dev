import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-dev-key')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'django_htmx',
    'django_celery_beat',
    'django_celery_results',
    'bootstrap5',
    # local apps
    'apps.core',
    'apps.theses',
    'apps.marketdata',
    'apps.news',
    'apps.alerts',
    'apps.geopolitics',
    'apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'geoportal'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),  # will be 'db' in Docker
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule (for periodic tasks)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'update-daily-prices': {
        'task': 'apps.marketdata.tasks.update_daily_prices',
        'schedule': crontab(hour=21, minute=0),  # 9pm GMT (market close)
    },
}

# Add LLM prediction generation to beat schedule
CELERY_BEAT_SCHEDULE.setdefault('generate-llm-predictions', {
    'task': 'apps.news.tasks.generate_llm_predictions',
    'schedule': crontab(hour=8, minute=0),  # daily at 8am
})

# Add evaluate predictions task to beat schedule
CELERY_BEAT_SCHEDULE.setdefault('evaluate-predictions', {
    'task': 'apps.theses.tasks.evaluate_predictions',
    'schedule': crontab(hour=22, minute=0),  # after market close
})

# Add weekly accuracy stats update to beat schedule
CELERY_BEAT_SCHEDULE.setdefault('update-accuracy-stats', {
    'task': 'apps.theses.utils.update_accuracy_stats',
    'schedule': crontab(day_of_week=0, hour=23, minute=0),  # Sunday 11pm
})

# Add daily risk allocation check to beat schedule
CELERY_BEAT_SCHEDULE.setdefault('check-risk-allocation', {
    'task': 'apps.alerts.tasks.check_risk_allocation',
    'schedule': crontab(hour=17, minute=0),  # daily after market close
})

# Add marketdata indicator and correlation update tasks
CELERY_BEAT_SCHEDULE.setdefault('update-technical-indicators', {
    'task': 'apps.marketdata.tasks.update_technical_indicators',
    'schedule': crontab(hour=20, minute=0),  # daily at 8pm
})

CELERY_BEAT_SCHEDULE.setdefault('update-correlation-matrix', {
    'task': 'apps.marketdata.tasks.update_correlation_matrix',
    'schedule': crontab(day_of_week=0, hour=21, minute=0),  # weekly on Sunday 9pm
})

# Add rebalance suggestion generation weekly
CELERY_BEAT_SCHEDULE.setdefault('generate-rebalance-suggestions', {
    'task': 'apps.alerts.tasks.generate_rebalance_suggestions',
    'schedule': crontab(day_of_week=0, hour=20, minute=0),  # weekly on Sunday 8pm
})


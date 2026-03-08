#!/usr/bin/env python3
"""
Soul-TrAIder Project Setup Script
Generates the complete Django project structure with initial files.
Run this script in an empty directory to bootstrap the project.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
PROJECT_NAME = "Soul-TrAIder"
BASE_DIR = Path(os.getcwd()) / PROJECT_NAME

# ------------------------------------------------------------
# File and directory definitions
# ------------------------------------------------------------
DIRS = [
    "config/settings",
    "apps/core/migrations",
    "apps/core/management/commands",
    "apps/theses/migrations",
    "apps/marketdata/migrations",
    "apps/marketdata/management/commands",
    "apps/news/migrations",
    "apps/alerts/migrations",
    "apps/dashboard/templates/dashboard/partials",
    "apps/dashboard/static/dashboard/css",
    "apps/dashboard/static/dashboard/js",
    "templates",
    "static",
    "media",
    "scripts",
]

FILES = {
    # Root files
    "requirements.txt": """Django==4.2.10
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
yfinance==0.2.37
pandas==2.2.1
celery==5.3.4
redis==5.0.1
django-celery-beat==2.5.0
django-celery-results==2.5.1
feedparser==6.0.10
beautifulsoup4==4.12.2
ollama==0.1.7
django-htmx==1.17.0
django-bootstrap5==23.3
""",
    ".env.example": """SECRET_KEY=your-secret-key-here
DB_NAME=geoportal
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
""",
    "README.md": f"# {PROJECT_NAME}\n\nGeopolitical investment tracker.\n",
    "manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",
    # Config files
    "config/__init__.py": "",
    "config/wsgi.py": """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
application = get_wsgi_application()
""",
    "config/urls.py": """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
]
""",
    "config/settings/__init__.py": "",
    "config/settings/base.py": """import os
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
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

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

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
""",
    "config/settings/dev.py": """from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
""",
    "config/settings/prod.py": """from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
""",
    # Apps __init__
    "apps/__init__.py": "",
    # Core app
    "apps/core/__init__.py": "",
    "apps/core/admin.py": "from django.contrib import admin\n# Register your models here.\n",
    "apps/core/apps.py": """from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
""",
    "apps/core/models.py": """from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Instrument(models.Model):
    ASSET_TYPES = [
        ('stock', 'Stock'),
        ('etf', 'ETF'),
        ('bond', 'Bond'),
        ('crypto', 'Cryptocurrency'),
    ]
    ticker = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    currency = models.CharField(max_length=3)  # e.g., 'GBP', 'USD'
    sector = models.CharField(max_length=50, blank=True)
    thesis = models.TextField(blank=True, help_text="Why you're interested in this instrument")

    def __str__(self):
        return f"{self.ticker} - {self.name}"

class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    platform = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    instruments = models.ManyToManyField(Instrument, through='Transaction')

    def __str__(self):
        return self.name

class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    buy_date = models.DateField()
    shares = models.DecimalField(max_digits=12, decimal_places=6)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    fees = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.portfolio} - {self.instrument} - {self.buy_date}"
""",
    "apps/core/migrations/__init__.py": "",
    # Theses app
    "apps/theses/__init__.py": "",
    "apps/theses/admin.py": "",
    "apps/theses/apps.py": """from django.apps import AppConfig

class ThesesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.theses'
""",
    "apps/theses/models.py": """from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Thesis(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ThesisInstrument(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ['instrument']})
    object_id = models.PositiveIntegerField()
    instrument = GenericForeignKey('content_type', 'object_id')
    weight = models.FloatField(default=1.0)

class Prediction(models.Model):
    PREDICTION_TYPES = [
        ('price_target', 'Price Target'),
        ('event', 'Event'),
    ]
    DIRECTION = [
        ('above', 'Above'),
        ('below', 'Below'),
    ]
    STATUS = [
        ('active', 'Active'),
        ('hit', 'Hit'),
        ('missed', 'Missed'),
        ('expired', 'Expired'),
    ]
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, null=True, blank=True)
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    target_date = models.DateField(null=True, blank=True)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    direction = models.CharField(max_length=10, choices=DIRECTION, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    confidence = models.DecimalField(max_digits=3, decimal_places=2)
    rationale = models.TextField()
    status = models.CharField(max_length=20, default='active', choices=STATUS)

    def __str__(self):
        return f"{self.instrument} - {self.created_date}"
""",
    "apps/theses/migrations/__init__.py": "",
    # Marketdata app
    "apps/marketdata/__init__.py": "",
    "apps/marketdata/admin.py": "",
    "apps/marketdata/apps.py": """from django.apps import AppConfig

class MarketdataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marketdata'
""",
    "apps/marketdata/models.py": """from django.db import models
from apps.core.models import Instrument

class DailyPrice(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date = models.DateField()
    close = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('instrument', 'date')

    def __str__(self):
        return f"{self.instrument.ticker} - {self.date}"
""",
    "apps/marketdata/utils.py": """import yfinance as yf
from .models import DailyPrice

def get_latest_price(ticker):
    # Try DB first
    latest = DailyPrice.objects.filter(instrument__ticker=ticker).order_by('-date').first()
    if latest:
        return latest.close
    # Otherwise fetch live
    try:
        tick = yf.Ticker(ticker)
        data = tick.history(period='1d')
        if not data.empty:
            return data['Close'].iloc[-1]
    except Exception:
        pass
    return None
""",
    "apps/marketdata/tasks.py": """from celery import shared_task
import yfinance as yf
from .models import DailyPrice
from apps.core.models import Instrument
from datetime import date

@shared_task
def update_daily_prices():
    instruments = Instrument.objects.all()
    today = date.today()
    for inst in instruments:
        try:
            tick = yf.Ticker(inst.ticker)
            hist = tick.history(period='1d')
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                DailyPrice.objects.update_or_create(
                    instrument=inst,
                    date=today,
                    defaults={'close': close}
                )
        except Exception as e:
            print(f"Error updating {inst.ticker}: {e}")
    return f"Updated {instruments.count()} instruments"
""",
    "apps/marketdata/migrations/__init__.py": "",
    # News app
    "apps/news/__init__.py": "",
    "apps/news/admin.py": "",
    "apps/news/apps.py": """from django.apps import AppConfig

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.news'
""",
    "apps/news/models.py": """from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.core.models import Instrument

class NewsArticle(models.Model):
    source = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True)
    keywords = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    def __str__(self):
        return self.title

class NewsImpact(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    sentiment = models.DecimalField(max_digits=3, decimal_places=2)  # -1 to 1
    summary = models.TextField()
    relevant = models.BooleanField(default=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'instrument')
""",
    "apps/news/scrapers.py": "# Placeholder for RSS scraping logic\n",
    "apps/news/llm.py": "# Placeholder for LLM analysis integration\n",
    "apps/news/migrations/__init__.py": "",
    # Alerts app
    "apps/alerts/__init__.py": "",
    "apps/alerts/admin.py": "",
    "apps/alerts/apps.py": """from django.apps import AppConfig

class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.alerts'
""",
    "apps/alerts/models.py": """from django.db import models
from apps.core.models import Instrument
from apps.theses.models import Prediction

class Alert(models.Model):
    ALERT_TYPES = [
        ('target', 'Target'),
        ('stop_loss', 'Stop Loss'),
        ('news', 'News'),
    ]
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    prediction = models.ForeignKey(Prediction, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=10, decimal_places=4)
    triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.instrument} - {self.alert_type}"
""",
    "apps/alerts/notifiers.py": "# Placeholder for Slack/email notifications\n",
    "apps/alerts/migrations/__init__.py": "",
    # Dashboard app
    "apps/dashboard/__init__.py": "",
    "apps/dashboard/admin.py": "",
    "apps/dashboard/apps.py": """from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'
""",
    "apps/dashboard/urls.py": """from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard-index'),
    path('holdings/', views.holdings, name='dashboard-holdings'),
    path('predictions/', views.predictions, name='dashboard-predictions'),
    path('news/', views.news, name='dashboard-news'),
    path('partials/holdings-table/', views.holdings_table, name='partial-holdings-table'),
    path('partials/price-update/<int:instrument_id>/', views.price_update, name='partial-price-update'),
]
""",
    "apps/dashboard/views.py": """from django.shortcuts import render
from django.http import HttpResponse
from apps.core.models import Transaction, Instrument
from apps.marketdata.utils import get_latest_price

def index(request):
    portfolios = Transaction.objects.values('portfolio__name').distinct()
    return render(request, 'dashboard/index.html', {'portfolios': portfolios})

def holdings(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio').all()
    return render(request, 'dashboard/holdings.html', {'transactions': transactions})

def predictions(request):
    return render(request, 'dashboard/predictions.html')

def news(request):
    return render(request, 'dashboard/news.html')

def holdings_table(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio').all()
    return render(request, 'dashboard/partials/holdings_table.html', {'transactions': transactions})

def price_update(request, instrument_id):
    instrument = Instrument.objects.get(id=instrument_id)
    price = get_latest_price(instrument.ticker)
    if price is None:
        price = 'N/A'
    return HttpResponse(f"{price} {instrument.currency}")
""",
    # Templates
    "templates/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Soul-TrAIder{% endblock %}</title>
    {% load bootstrap5 %}
    {% bootstrap_css %}
    {% bootstrap_javascript %}
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    {% block extra_head %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'dashboard-index' %}">Soul-TrAIder</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'dashboard-holdings' %}">Holdings</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'dashboard-predictions' %}">Predictions</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'dashboard-news' %}">News</a></li>
                </ul>
            </div>
        </div>
    </nav>
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
""",
    "apps/dashboard/templates/dashboard/index.html": """{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<h1>Portfolio Overview</h1>
<div hx-get="{% url 'partial-holdings-table' %}" hx-trigger="load, every 30s" hx-swap="innerHTML">
    Loading holdings...
</div>
{% endblock %}
""",
    "apps/dashboard/templates/dashboard/holdings.html": """{% extends "base.html" %}
{% block title %}Holdings{% endblock %}
{% block content %}
<h1>Detailed Holdings</h1>
{% include "dashboard/partials/holdings_table.html" %}
{% endblock %}
""",
    "apps/dashboard/templates/dashboard/partials/holdings_table.html": """<table class="table table-striped">
    <thead>
        <tr>
            <th>Portfolio</th>
            <th>Ticker</th>
            <th>Shares</th>
            <th>Entry Price</th>
            <th>Current Price</th>
            <th>Value</th>
            <th>Return</th>
        </tr>
    </thead>
    <tbody>
        {% for tx in transactions %}
        <tr>
            <td>{{ tx.portfolio.name }}</td>
            <td>{{ tx.instrument.ticker }}</td>
            <td>{{ tx.shares }}</td>
            <td>{{ tx.price_per_share }}</td>
            <td hx-get="{% url 'partial-price-update' tx.instrument.id %}" hx-trigger="load, every 60s" hx-swap="innerHTML">Loading...</td>
            <td id="value-{{ tx.instrument.id }}"></td>
            <td id="return-{{ tx.instrument.id }}"></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
""",
    "apps/dashboard/templates/dashboard/predictions.html": """{% extends "base.html" %}
{% block title %}Predictions{% endblock %}
{% block content %}
<h1>Prediction Tracker</h1>
<p>Coming soon...</p>
{% endblock %}
""",
    "apps/dashboard/templates/dashboard/news.html": """{% extends "base.html" %}
{% block title %}News{% endblock %}
{% block content %}
<h1>Geopolitical News</h1>
<p>Coming soon...</p>
{% endblock %}
""",
    # Scripts
    "scripts/load_initial_data.py": """#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.core.models import Instrument, Portfolio, Transaction

# Instruments
instruments_data = [
    {'ticker': 'HBR.L', 'name': 'Harbour Energy', 'asset_type': 'stock', 'currency': 'GBP', 'sector': 'energy'},
    {'ticker': 'BA.L', 'name': 'BAE Systems', 'asset_type': 'stock', 'currency': 'GBP', 'sector': 'defense'},
    {'ticker': 'NIO', 'name': 'NIO Inc.', 'asset_type': 'stock', 'currency': 'USD', 'sector': 'ev'},
    {'ticker': 'SQZ.L', 'name': 'Serica Energy', 'asset_type': 'stock', 'currency': 'GBP', 'sector': 'energy'},
    {'ticker': 'WATR.L', 'name': 'Water Intelligence', 'asset_type': 'stock', 'currency': 'GBP', 'sector': 'water'},
    {'ticker': 'KSA', 'name': 'Franklin FTSE Saudi Arabia ETF', 'asset_type': 'etf', 'currency': 'USD', 'sector': 'gcc'},
    {'ticker': 'SVT.L', 'name': 'Severn Trent', 'asset_type': 'stock', 'currency': 'GBP', 'sector': 'water'},
]

for data in instruments_data:
    Instrument.objects.get_or_create(**data)

# Portfolios
freetrade, _ = Portfolio.objects.get_or_create(name='Freetrade', platform='Freetrade')
t212, _ = Portfolio.objects.get_or_create(name='Trading212', platform='Trading212')

# Transactions (adjust dates/prices as needed)
Transaction.objects.get_or_create(
    portfolio=freetrade,
    instrument=Instrument.objects.get(ticker='HBR.L'),
    buy_date='2026-03-05',
    shares=16,
    price_per_share=2.22,
)
Transaction.objects.get_or_create(
    portfolio=freetrade,
    instrument=Instrument.objects.get(ticker='BA.L'),
    buy_date='2026-03-05',
    shares=1,
    price_per_share=22.00,
)
Transaction.objects.get_or_create(
    portfolio=freetrade,
    instrument=Instrument.objects.get(ticker='NIO'),
    buy_date='2026-03-05',
    shares=5.68,
    price_per_share=4.78,
)
Transaction.objects.get_or_create(
    portfolio=freetrade,
    instrument=Instrument.objects.get(ticker='SQZ.L'),
    buy_date='2026-03-05',
    shares=7,
    price_per_share=2.00,
)
# Portfolio 2 orders (pending)
Transaction.objects.get_or_create(
    portfolio=t212,
    instrument=Instrument.objects.get(ticker='WATR.L'),
    buy_date='2026-03-07',
    shares=13.02,
    price_per_share=3.07,
)
Transaction.objects.get_or_create(
    portfolio=t212,
    instrument=Instrument.objects.get(ticker='KSA'),
    buy_date='2026-03-07',
    shares=2.14,
    price_per_share=23.64,
)
Transaction.objects.get_or_create(
    portfolio=t212,
    instrument=Instrument.objects.get(ticker='SVT.L'),
    buy_date='2026-03-07',
    shares=0.64,
    price_per_share=31.52,
)

print("Initial data loaded.")
""",
}

# ------------------------------------------------------------
# Helper to create directory and file
# ------------------------------------------------------------
def create_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    print(f"Creating project {PROJECT_NAME} in {BASE_DIR}...")
    BASE_DIR.mkdir(exist_ok=True)
    os.chdir(BASE_DIR)

    # Create directories
    for d in DIRS:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)

    # Create files
    for rel_path, content in FILES.items():
        full_path = BASE_DIR / rel_path
        create_file(full_path, content)
        print(f"  Created {rel_path}")

    print("\nProject structure created successfully!")
    print("\nNext steps:")
    print("1. Create a virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("3. Copy .env.example to .env and edit with your database credentials")
    print("4. Create PostgreSQL database (e.g., 'geoportal')")
    print("5. Run migrations:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print("6. Load initial data:")
    print("   python scripts/load_initial_data.py")
    print("7. Create a superuser for admin:")
    print("   python manage.py createsuperuser")
    print("8. Run development server:")
    print("   python manage.py runserver")
    print("\nVisit http://127.0.0.1:8000 to see your dashboard.")

if __name__ == '__main__':
    main()
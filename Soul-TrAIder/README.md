📄 README.md – Project Overview
markdown

# Soul-TrAIder

A geopolitical investment thesis tracker that helps you manage portfolios based on global events, track predictions, and monitor news with AI-powered analysis.

## 🎯 Purpose

Soul-TrAIder is built around a core investment philosophy: **geopolitical events drive markets, and a disciplined, thesis-driven approach can capture asymmetric returns**. The system allows you to:

- Track multiple portfolios and instruments
- Define investment theses and link instruments to them
- Make price and event-based predictions with clear targets
- Automatically fetch daily prices and monitor thresholds
- Scrape and analyze geopolitical news with LLM sentiment scoring
- Receive alerts when targets/stops are hit or critical news breaks

## 🏗️ Architecture

The project is a modular Django application with the following apps:

- **core**: Base models (Instrument, Portfolio, Transaction)
- **theses**: Thesis definitions and predictions
- **marketdata**: Price fetching and storage (yfinance)
- **news**: RSS scraping and LLM analysis (Ollama)
- **alerts**: Threshold monitoring and notifications
- **dashboard**: Frontend views with HTMX for dynamic updates

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (for Celery)
- Ollama (optional, for local LLM analysis)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Git-Lister/SoulTrAIder-dev.git
   cd SoulTrAIder-dev/Soul-TrAIder
   Create and activate virtual environment
   ```

bash
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Copy environment template

bash
cp .env.example .env

# Edit .env with your database credentials

Create PostgreSQL database

sql
CREATE DATABASE geoportal;
Run migrations

bash
python manage.py makemigrations
python manage.py migrate
Load initial portfolio data

bash
python scripts/load_initial_data.py
Create superuser for admin

bash
python manage.py createsuperuser
Run development server

bash
python manage.py runserver
Visit http://127.0.0.1:8000 to see your dashboard

📊 Current Status
Phase 0 (Foundation) is complete:

✅ Django project structure

✅ Core models (Instrument, Portfolio, Transaction)

✅ Basic dashboard with HTMX live price updates

✅ Initial data loaded from your two portfolios

See PROGRESS.md for detailed development status and next steps.

🔮 Roadmap
Phase 1: Celery integration + automated daily price updates

Phase 2: Prediction models + alert engine

Phase 3: News scraping + LLM analysis

Phase 4: Enhanced dashboard with charts and thesis tracking

🤝 Contributing
This is a personal project, but suggestions and ideas are welcome via Issues.

📝 License
MIT

#!/usr/bin/env python
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

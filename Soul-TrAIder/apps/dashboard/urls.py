from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='dashboard-index'),
    path('holdings/', views.holdings, name='dashboard-holdings'),
    path('predictions/', views.predictions, name='dashboard-predictions'),
    path('predictions/llm/', views.predictions_llm, name='dashboard-predictions-llm'),
    path('news/', views.news, name='dashboard-news'),
    path('partials/holdings-table/', views.holdings_table, name='partial-holdings-table'),
    path('partials/price-update/<int:instrument_id>/', views.price_update, name='partial-price-update'),
    path('accuracy/', views.accuracy_stats, name='dashboard-accuracy'),
    path('hypothetical/', views.hypothetical_portfolio, name='dashboard-hypothetical'),
    path('journal/', views.trading_journal, name='dashboard-journal'),
]

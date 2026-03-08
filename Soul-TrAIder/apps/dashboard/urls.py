from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard-index'),
    path('holdings/', views.holdings, name='dashboard-holdings'),
    path('predictions/', views.predictions, name='dashboard-predictions'),
    path('news/', views.news, name='dashboard-news'),
    path('partials/holdings-table/', views.holdings_table, name='partial-holdings-table'),
    path('partials/price-update/<int:instrument_id>/', views.price_update, name='partial-price-update'),
]

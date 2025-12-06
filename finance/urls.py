from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('expenses/', views.ExpensesView.as_view(), name='expenses'),
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('currency/', views.CurrencyView.as_view(), name='currency'),
]

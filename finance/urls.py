from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('expenses/', views.ExpensesView.as_view(), name='expenses'),
    path('expenses/export/', views.export_expenses_excel, name='export_expenses_excel'),
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('payments/export/', views.export_payments_excel, name='export_payments_excel'),
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('calculator/export/', views.export_calculator_excel, name='export_calculator_excel'),
    path('currency/', views.CurrencyView.as_view(), name='currency'),
]

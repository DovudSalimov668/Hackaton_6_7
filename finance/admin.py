from django.contrib import admin
from .models import Transaction, PaymentSchedule, CurrencyRate


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'category', 'amount', 'description']
    list_filter = ['category', 'date']
    search_fields = ['description']
    date_hierarchy = 'date'


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ['due_date', 'planned_amount', 'is_paid', 'paid_amount', 'description']
    list_filter = ['is_paid', 'due_date']
    search_fields = ['description']
    date_hierarchy = 'due_date'


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ['date', 'currency_code', 'buy_rate', 'sell_rate']
    list_filter = ['currency_code', 'date']
    date_hierarchy = 'date'

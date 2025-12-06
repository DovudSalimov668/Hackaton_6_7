"""
Views для финансовых инструментов
"""
import json
from django.shortcuts import render
from django.views.generic import TemplateView
from . import services
from .models import PaymentSchedule


class ExpensesView(TemplateView):
    """Кейс 4: Анализ расходов"""
    template_name = 'expenses.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем данные анализа расходов
        analysis = services.analyze_expenses()
        
        context['total_expenses'] = analysis['total']
        context['categories'] = analysis['categories']
        
        # Данные для Pie Chart (в JSON для JavaScript)
        context['chart_data'] = json.dumps({
            'labels': analysis['labels'],
            'data': analysis['data'],
            'colors': analysis['colors'],
        }, ensure_ascii=False)
        
        return context


class PaymentsView(TemplateView):
    """Кейс 5: Напоминания о платежах"""
    template_name = 'payments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем ближайший платеж
        upcoming = services.get_upcoming_payment()
        context['upcoming'] = upcoming
        
        # Получаем просроченные платежи
        overdue = services.get_overdue_payments()
        context['overdue'] = overdue
        
        # Весь график платежей
        context['all_payments'] = PaymentSchedule.objects.all()
        
        return context


class CalculatorView(TemplateView):
    """Кейс 6: Кредитный калькулятор"""
    template_name = 'calculator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Значения по умолчанию
        context['amount'] = 100000
        context['months'] = 12
        context['rate'] = 15.0
        
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        # Получаем параметры из формы
        try:
            amount = float(request.POST.get('amount', 100000))
            months = int(request.POST.get('months', 12))
            rate = float(request.POST.get('rate', 15.0))
            
            # Валидация
            amount = max(100, min(500000, amount))
            months = max(1, min(120, months))
            rate = max(1, min(35, rate))
            
            context['amount'] = amount
            context['months'] = months
            context['rate'] = rate
            
            # Расчет обоих типов кредита
            comparison = services.calculate_loan_comparison(amount, months, rate)
            
            context['annuity_schedule'] = comparison['annuity']
            context['diff_schedule'] = comparison['differentiated']
            context['annuity_total'] = comparison['annuity_total']
            context['annuity_overpayment'] = comparison['annuity_overpayment']
            context['diff_total'] = comparison['diff_total']
            context['diff_overpayment'] = comparison['diff_overpayment']
            
            # Данные для графиков
            # 1. Stacked Bar Chart - платежи по месяцам для аннуитета
            annuity_labels = [f"Мес. {p['month']}" for p in comparison['annuity']]
            annuity_principal = [p['principal'] for p in comparison['annuity']]
            annuity_interest = [p['interest'] for p in comparison['annuity']]
            
            context['annuity_chart_data'] = json.dumps({
                'labels': annuity_labels,
                'principal': annuity_principal,
                'interest': annuity_interest,
            }, ensure_ascii=False)
            
            # 2. Stacked Bar Chart - платежи по месяцам для дифференцированного
            diff_labels = [f"Мес. {p['month']}" for p in comparison['differentiated']]
            diff_principal = [p['principal'] for p in comparison['differentiated']]
            diff_interest = [p['interest'] for p in comparison['differentiated']]
            
            context['diff_chart_data'] = json.dumps({
                'labels': diff_labels,
                'principal': diff_principal,
                'interest': diff_interest,
            }, ensure_ascii=False)
            
            # 3. Сравнительный Line Chart - общие платежи
            comparison_payments_annuity = [p['payment'] for p in comparison['annuity']]
            comparison_payments_diff = [p['payment'] for p in comparison['differentiated']]
            
            context['comparison_chart_data'] = json.dumps({
                'labels': annuity_labels,
                'annuity': comparison_payments_annuity,
                'differentiated': comparison_payments_diff,
            }, ensure_ascii=False)
            
        except (ValueError, TypeError) as e:
            context['error'] = 'Ошибка в параметрах расчета'
        
        return render(request, self.template_name, context)


class CurrencyView(TemplateView):
    """Кейс 7: Обмен валют"""
    template_name = 'currency.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Значения по умолчанию
        context['amount'] = 100
        context['currency'] = 'USD'
        context['operation'] = 'buy'
        context['history_days'] = 30
        
        # Прогноз курса USD
        usd_forecast = services.get_currency_forecast('USD', days=7)
        context['usd_forecast'] = usd_forecast
        
        # Прогноз курса EUR
        eur_forecast = services.get_currency_forecast('EUR', days=7)
        context['eur_forecast'] = eur_forecast
        
        # История курсов для графика (по умолчанию 30 дней)
        usd_history = services.get_currency_history('USD', days=30)
        context['usd_history'] = json.dumps(usd_history, ensure_ascii=False)
        
        eur_history = services.get_currency_history('EUR', days=30)
        context['eur_history'] = json.dumps(eur_history, ensure_ascii=False)
        
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        # Конвертация валюты
        try:
            amount = float(request.POST.get('amount', 100))
            currency = request.POST.get('currency', 'USD')
            operation = request.POST.get('operation', 'buy')
            history_days = int(request.POST.get('history_days', 30))
            
            context['amount'] = amount
            context['currency'] = currency
            context['operation'] = operation
            context['history_days'] = history_days
            
            # Выполняем конвертацию
            conversion = services.convert_currency(amount, currency, operation)
            context['conversion'] = conversion
            
            # Обновляем историю курсов для выбранного периода
            usd_history = services.get_currency_history('USD', days=history_days)
            context['usd_history'] = json.dumps(usd_history, ensure_ascii=False)
            
            eur_history = services.get_currency_history('EUR', days=history_days)
            context['eur_history'] = json.dumps(eur_history, ensure_ascii=False)
            
        except (ValueError, TypeError) as e:
            context['error'] = 'Ошибка в параметрах конвертации'
        
        return render(request, self.template_name, context)

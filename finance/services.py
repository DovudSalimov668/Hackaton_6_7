"""
Бизнес-логика для финансовых инструментов
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum
from .models import Transaction, PaymentSchedule, CurrencyRate


# ============================================
# КЕЙС 4: Анализ расходов
# ============================================

def analyze_expenses():
    """
    Анализирует транзакции и возвращает данные для Pie Chart
    Returns: dict с labels, data, colors для Chart.js
    """
    # Группировка по категориям
    category_totals = Transaction.objects.values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Цвета для каждой категории
    colors = {
        'Food': '#FF6384',
        'Transport': '#36A2EB',
        'Communication': '#FFCE56',
        'Entertainment': '#4BC0C0',
        'Shopping': '#9966FF',
        'Bills': '#FF9F40',
        'Other': '#C9CBCF',
    }
    
    labels = []
    data = []
    background_colors = []
    
    for item in category_totals:
        category = item['category']
        total = float(item['total'])
        labels.append(dict(Transaction.CATEGORY_CHOICES).get(category, category))
        data.append(total)
        background_colors.append(colors.get(category, '#999999'))
    
    # Общая сумма расходов
    total_expenses = sum(data)
    
    return {
        'labels': labels,
        'data': data,
        'colors': background_colors,
        'total': total_expenses,
        'categories': [
            {
                'name': dict(Transaction.CATEGORY_CHOICES).get(item['category'], item['category']),
                'amount': float(item['total']),
                'percentage': round(float(item['total']) / total_expenses * 100, 1) if total_expenses > 0 else 0
            }
            for item in category_totals
        ]
    }


# ============================================
# КЕЙС 5: Напоминания о платежах
# ============================================

def get_upcoming_payment():
    """
    Находит ближайший предстоящий платеж
    Returns: dict с информацией о платеже и уровнем алерта
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Ищем ближайший неоплаченный платеж
    upcoming = PaymentSchedule.objects.filter(
        due_date__gte=today,
        is_paid=False
    ).order_by('due_date').first()
    
    if not upcoming:
        return None
    
    days_until = (upcoming.due_date - today).days
    
    # Определяем уровень алерта
    if days_until == 0:
        alert_level = 'danger'  # сегодня
        alert_message = 'Сегодня'
    elif days_until == 1:
        alert_level = 'warning'  # завтра
        alert_message = 'Завтра'
    elif days_until <= 7:
        alert_level = 'info'  # на этой неделе
        alert_message = f'Через {days_until} дн.'
    else:
        alert_level = 'success'  # далеко
        alert_message = f'Через {days_until} дн.'
    
    return {
        'payment': upcoming,
        'days_until': days_until,
        'alert_level': alert_level,
        'alert_message': alert_message,
    }


def get_overdue_payments():
    """
    Находит просроченные платежи
    Returns: dict с суммой долга и списком просроченных платежей
    """
    today = date.today()
    
    # Логика просрочки: today > due_date И (не оплачено ИЛИ оплачено меньше)
    overdue = PaymentSchedule.objects.filter(
        due_date__lt=today
    ).exclude(
        is_paid=True,
        paid_amount__gte=models.F('planned_amount')
    )
    
    total_debt = Decimal('0')
    overdue_list = []
    
    for payment in overdue:
        debt = payment.debt_amount
        total_debt += debt
        overdue_list.append({
            'payment': payment,
            'debt': debt,
        })
    
    return {
        'total_debt': total_debt,
        'overdue_payments': overdue_list,
        'count': len(overdue_list),
    }


# ============================================
# КЕЙС 6: Кредитный калькулятор
# ============================================

def calculate_annuity_loan(amount, months, annual_rate):
    """
    Расчет аннуитетного кредита
    Args:
        amount: сумма кредита
        months: срок в месяцах
        annual_rate: годовая ставка в процентах
    Returns: список платежей по месяцам
    """
    amount = Decimal(str(amount))
    months = int(months)
    monthly_rate = Decimal(str(annual_rate)) / Decimal('100') / Decimal('12')
    
    if monthly_rate == 0:
        # Если ставка 0%, просто делим сумму на месяцы
        monthly_payment = amount / months
        schedule = []
        for month in range(1, months + 1):
            schedule.append({
                'month': month,
                'payment': float(monthly_payment),
                'principal': float(monthly_payment),
                'interest': 0,
                'remaining': float(amount - monthly_payment * month),
            })
        return schedule
    
    # Формула аннуитетного платежа
    # P = S * (r * (1 + r)^n) / ((1 + r)^n - 1)
    coefficient = (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    monthly_payment = amount * coefficient
    
    schedule = []
    remaining_balance = amount
    
    for month in range(1, months + 1):
        # Проценты за месяц
        interest_payment = remaining_balance * monthly_rate
        # Тело долга
        principal_payment = monthly_payment - interest_payment
        # Остаток
        remaining_balance -= principal_payment
        
        schedule.append({
            'month': month,
            'payment': float(monthly_payment),
            'principal': float(principal_payment),
            'interest': float(interest_payment),
            'remaining': float(max(0, remaining_balance)),
        })
    
    return schedule


def calculate_differentiated_loan(amount, months, annual_rate):
    """
    Расчет дифференцированного кредита
    Args:
        amount: сумма кредита
        months: срок в месяцах
        annual_rate: годовая ставка в процентах
    Returns: список платежей по месяцам
    """
    amount = Decimal(str(amount))
    months = int(months)
    monthly_rate = Decimal(str(annual_rate)) / Decimal('100') / Decimal('12')
    
    # Фиксированная часть (тело долга)
    principal_payment = amount / months
    
    schedule = []
    remaining_balance = amount
    
    for month in range(1, months + 1):
        # Проценты на остаток долга
        interest_payment = remaining_balance * monthly_rate
        # Общий платеж
        total_payment = principal_payment + interest_payment
        # Уменьшаем остаток
        remaining_balance -= principal_payment
        
        schedule.append({
            'month': month,
            'payment': float(total_payment),
            'principal': float(principal_payment),
            'interest': float(interest_payment),
            'remaining': float(max(0, remaining_balance)),
        })
    
    return schedule


def calculate_loan_comparison(amount, months, rate):
    """
    Сравнение двух типов кредита
    Returns: данные для графиков сравнения
    """
    annuity = calculate_annuity_loan(amount, months, rate)
    differentiated = calculate_differentiated_loan(amount, months, rate)
    
    # Общие переплаты
    annuity_overpayment = sum(p['interest'] for p in annuity)
    diff_overpayment = sum(p['interest'] for p in differentiated)
    
    return {
        'annuity': annuity,
        'differentiated': differentiated,
        'annuity_total': sum(p['payment'] for p in annuity),
        'annuity_overpayment': annuity_overpayment,
        'diff_total': sum(p['payment'] for p in differentiated),
        'diff_overpayment': diff_overpayment,
    }


# ============================================
# КЕЙС 7: Валютный конвертер
# ============================================

def get_currency_forecast(currency_code, days=7):
    """
    Простой прогноз курса на основе среднего за последние N дней
    Args:
        currency_code: USD или EUR
        days: количество дней для анализа
    Returns: прогнозируемый курс
    """
    recent_rates = CurrencyRate.objects.filter(
        currency_code=currency_code
    ).order_by('-date')[:days]
    
    if not recent_rates:
        return None
    
    # Среднее значение покупки и продажи
    avg_buy = sum(r.buy_rate for r in recent_rates) / len(recent_rates)
    avg_sell = sum(r.sell_rate for r in recent_rates) / len(recent_rates)
    
    return {
        'buy_forecast': round(float(avg_buy), 4),
        'sell_forecast': round(float(avg_sell), 4),
        'avg_rate': round(float((avg_buy + avg_sell) / 2), 4),
    }


def convert_currency(amount, currency_code, operation='buy'):
    """
    Конвертация валюты
    Args:
        amount: сумма для конвертации
        currency_code: USD или EUR
        operation: 'buy' (покупка валюты) или 'sell' (продажа валюты)
    Returns: результат конвертации
    """
    # Получаем последний курс
    latest_rate = CurrencyRate.objects.filter(
        currency_code=currency_code
    ).order_by('-date').first()
    
    if not latest_rate:
        return None
    
    amount = Decimal(str(amount))
    
    if operation == 'buy':
        # Покупаем валюту (используем курс продажи банка)
        rate = latest_rate.sell_rate
        result = amount * rate
        explanation = f"Курс продажи: {rate} руб."
    else:
        # Продаем валюту (используем курс покупки банка)
        rate = latest_rate.buy_rate
        result = amount * rate
        explanation = f"Курс покупки: {rate} руб."
    
    return {
        'amount': float(amount),
        'rate': float(rate),
        'result': float(result),
        'currency': currency_code,
        'operation': operation,
        'explanation': explanation,
    }


def get_currency_history(currency_code, days=30):
    """
    Получить историю курсов валюты
    Args:
        currency_code: USD или EUR
        days: количество дней истории
    Returns: данные для графика
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    rates = CurrencyRate.objects.filter(
        currency_code=currency_code,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    labels = []
    buy_data = []
    sell_data = []
    
    for rate in rates:
        labels.append(rate.date.strftime('%d.%m'))
        buy_data.append(float(rate.buy_rate))
        sell_data.append(float(rate.sell_rate))
    
    return {
        'labels': labels,
        'buy_data': buy_data,
        'sell_data': sell_data,
    }


# Исправление импорта для get_overdue_payments
from django.db import models

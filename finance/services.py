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
    Кейс 4: Анализ расходов клиентов
    Загрузка CSV, классификация, подсчёт долей
    """
    import csv
    import os
    from collections import defaultdict
    
    # Пути к файлам
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_data_dir = os.path.join(base_dir, 'mock_data')
    
    # Загружаем категории
    categories = {}
    try:
        categories_file = os.path.join(mock_data_dir, 'transaction_categories.csv')
        with open(categories_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat_id = int(row['category_id'])
                categories[cat_id] = {
                    'id': cat_id,
                    'name': row['category_name'],
                    'is_expense': row['is_expense'].lower() == 't'
                }
    except Exception as e:
        print(f"CSV Error loading categories: {e}")
        categories = {}
    
    # Загружаем транзакции
    transactions = []
    try:
        transactions_file = os.path.join(mock_data_dir, 'transactions.csv')
        with open(transactions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['is_cancelled'].lower() == 't':
                    continue
                cat_id = int(row['category_id']) if row['category_id'] else None
                if cat_id and cat_id in categories and categories[cat_id]['is_expense']:
                    transactions.append({
                        'category_id': cat_id,
                        'amount': float(row['amount'])
                    })
    except Exception as e:
        print(f"CSV Error loading transactions: {e}")
        transactions = []
    
    # Группируем по категориям
    category_totals = defaultdict(float)
    for trans in transactions:
        category_totals[trans['category_id']] += trans['amount']
    
    # Сортируем по сумме
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Общая сумма
    total_expenses = sum(category_totals.values())
    
    # Подготовка данных
    colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', 
              '#6f42c1', '#fd7e14', '#20c997', '#e83e8c', '#6c757d']
    labels = []
    data = []
    background_colors = []
    categories_list = []
    
    for idx, (cat_id, total) in enumerate(sorted_cats):
        cat_name = categories[cat_id]['name']
        percentage = round((total / total_expenses * 100), 1) if total_expenses > 0 else 0
        
        labels.append(cat_name)
        data.append(total)
        background_colors.append(colors[idx % len(colors)])
        
        categories_list.append({
            'name': cat_name,
            'amount': total,
            'percentage': percentage
        })
    
    return {
        'labels': labels,
        'data': data,
        'colors': background_colors,
        'total': total_expenses,
        'categories': categories_list
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

def calculate_annuity_loan(amount, months, annual_rate, one_time_commission=0, monthly_commission=0):
    """
    Расчет аннуитетного кредита с комиссиями
    Args:
        amount: сумма кредита
        months: срок в месяцах
        annual_rate: годовая ставка в процентах
        one_time_commission: единовременная комиссия (0-5%)
        monthly_commission: ежемесячная комиссия (0-2%)
    Returns: список платежей по месяцам
    """
    amount = Decimal(str(amount))
    months = int(months)
    one_time_commission = Decimal(str(one_time_commission))
    monthly_commission = Decimal(str(monthly_commission))
    monthly_rate = Decimal(str(annual_rate)) / Decimal('100') / Decimal('12')
    
    # Применяем единовременную комиссию
    commission_amount = amount * (one_time_commission / Decimal('100'))
    loan_amount_with_commission = amount + commission_amount
    
    if monthly_rate == 0:
        # Если ставка 0%, просто делим сумму на месяцы
        monthly_payment = loan_amount_with_commission / months
        monthly_commission_amount = amount * (monthly_commission / Decimal('100'))
        
        schedule = []
        for month in range(1, months + 1):
            total_payment = monthly_payment + monthly_commission_amount
            schedule.append({
                'month': month,
                'payment': float(total_payment),
                'principal': float(monthly_payment),
                'interest': 0,
                'monthly_commission': float(monthly_commission_amount),
                'remaining': float(loan_amount_with_commission - monthly_payment * month),
            })
        return schedule, float(commission_amount)
    
    # Формула аннуитетного платежа
    # P = S * (r * (1 + r)^n) / ((1 + r)^n - 1)
    coefficient = (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    monthly_payment = loan_amount_with_commission * coefficient
    
    # Ежемесячная комиссия от исходной суммы
    monthly_commission_amount = amount * (monthly_commission / Decimal('100'))
    
    schedule = []
    remaining_balance = loan_amount_with_commission
    
    for month in range(1, months + 1):
        # Проценты за месяц
        interest_payment = remaining_balance * monthly_rate
        # Тело долга
        principal_payment = monthly_payment - interest_payment
        # Общий платеж с ежемесячной комиссией
        total_payment = monthly_payment + monthly_commission_amount
        # Остаток
        remaining_balance -= principal_payment
        
        schedule.append({
            'month': month,
            'payment': float(total_payment),
            'principal': float(principal_payment),
            'interest': float(interest_payment),
            'monthly_commission': float(monthly_commission_amount),
            'remaining': float(max(0, remaining_balance)),
        })
    
    return schedule, float(commission_amount)


def calculate_differentiated_loan(amount, months, annual_rate, one_time_commission=0, monthly_commission=0):
    """
    Расчет дифференцированного кредита с комиссиями
    Args:
        amount: сумма кредита
        months: срок в месяцах
        annual_rate: годовая ставка в процентах
        one_time_commission: единовременная комиссия (0-5%)
        monthly_commission: ежемесячная комиссия (0-2%)
    Returns: список платежей по месяцам
    """
    amount = Decimal(str(amount))
    months = int(months)
    one_time_commission = Decimal(str(one_time_commission))
    monthly_commission = Decimal(str(monthly_commission))
    monthly_rate = Decimal(str(annual_rate)) / Decimal('100') / Decimal('12')
    
    # Применяем единовременную комиссию
    commission_amount = amount * (one_time_commission / Decimal('100'))
    loan_amount_with_commission = amount + commission_amount
    
    # Фиксированная часть (тело долга)
    principal_payment = loan_amount_with_commission / months
    
    # Ежемесячная комиссия от исходной суммы
    monthly_commission_amount = amount * (monthly_commission / Decimal('100'))
    
    schedule = []
    remaining_balance = loan_amount_with_commission
    
    for month in range(1, months + 1):
        # Проценты на остаток долга
        interest_payment = remaining_balance * monthly_rate
        # Платеж без ежемесячной комиссии
        base_payment = principal_payment + interest_payment
        # Общий платеж с ежемесячной комиссией
        total_payment = base_payment + monthly_commission_amount
        # Уменьшаем остаток
        remaining_balance -= principal_payment
        
        schedule.append({
            'month': month,
            'payment': float(total_payment),
            'principal': float(principal_payment),
            'interest': float(interest_payment),
            'monthly_commission': float(monthly_commission_amount),
            'remaining': float(max(0, remaining_balance)),
        })
    
    return schedule, float(commission_amount)


def calculate_loan_comparison(amount, months, rate, one_time_commission=0, monthly_commission=0):
    """
    Сравнение двух типов кредита с комиссиями
    Returns: данные для графиков сравнения
    """
    annuity, annuity_one_time = calculate_annuity_loan(amount, months, rate, one_time_commission, monthly_commission)
    differentiated, diff_one_time = calculate_differentiated_loan(amount, months, rate, one_time_commission, monthly_commission)
    
    # Общие переплаты
    annuity_interest = sum(p['interest'] for p in annuity)
    diff_interest = sum(p['interest'] for p in differentiated)
    
    # Комиссии
    annuity_monthly_comm = sum(p['monthly_commission'] for p in annuity)
    diff_monthly_comm = sum(p['monthly_commission'] for p in differentiated)
    
    # Общие переплаты включая комиссии
    annuity_overpayment = annuity_interest + annuity_one_time + annuity_monthly_comm
    diff_overpayment = diff_interest + diff_one_time + diff_monthly_comm
    
    return {
        'annuity': annuity,
        'differentiated': differentiated,
        'annuity_total': sum(p['payment'] for p in annuity) + annuity_one_time,
        'annuity_overpayment': annuity_overpayment,
        'annuity_interest': annuity_interest,
        'annuity_one_time_commission': annuity_one_time,
        'annuity_monthly_commission': annuity_monthly_comm,
        'diff_total': sum(p['payment'] for p in differentiated) + diff_one_time,
        'diff_overpayment': diff_overpayment,
        'diff_interest': diff_interest,
        'diff_one_time_commission': diff_one_time,
        'diff_monthly_commission': diff_monthly_comm,
        'original_amount': float(amount),
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

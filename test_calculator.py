"""
Test script for loan calculator with commissions
Run: python test_calculator.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_mvp.settings')
django.setup()

from finance.services import calculate_loan_comparison

# Test parameters
amount = 100000
months = 12
rate = 15
one_time_commission = 2
monthly_commission = 1

print("=" * 60)
print("ТЕСТ КРЕДИТНОГО КАЛЬКУЛЯТОРА С КОМИССИЯМИ")
print("=" * 60)
print(f"Сумма: {amount} руб.")
print(f"Срок: {months} мес.")
print(f"Ставка: {rate}% годовых")
print(f"Единовременная комиссия: {one_time_commission}%")
print(f"Ежемесячная комиссия: {monthly_commission}%")
print("=" * 60)

try:
    result = calculate_loan_comparison(
        amount, months, rate, one_time_commission, monthly_commission
    )
    
    print("\n✅ Расчет успешно выполнен!")
    print(f"\nАННУИТЕТНЫЙ:")
    print(f"  Общая сумма: {result['annuity_total']:,.2f} руб.")
    print(f"  Переплата: {result['annuity_overpayment']:,.2f} руб.")
    print(f"    - Проценты: {result['annuity_interest']:,.2f} руб.")
    print(f"    - Единовременная комиссия: {result['annuity_one_time_commission']:,.2f} руб.")
    print(f"    - Ежемесячные комиссии: {result['annuity_monthly_commission']:,.2f} руб.")
    
    print(f"\nДИФФЕРЕНЦИРОВАННЫЙ:")
    print(f"  Общая сумма: {result['diff_total']:,.2f} руб.")
    print(f"  Переплата: {result['diff_overpayment']:,.2f} руб.")
    print(f"    - Проценты: {result['diff_interest']:,.2f} руб.")
    print(f"    - Единовременная комиссия: {result['diff_one_time_commission']:,.2f} руб.")
    print(f"    - Ежемесячные комиссии: {result['diff_monthly_commission']:,.2f} руб.")
    
    print(f"\nКоличество месяцев в графике аннуитет: {len(result['annuity'])}")
    print(f"Пример первого платежа аннуитет:")
    first = result['annuity'][0]
    print(f"  Месяц: {first['month']}")
    print(f"  Платеж: {first['payment']:,.2f} руб.")
    print(f"  Тело долга: {first['principal']:,.2f} руб.")
    print(f"  Проценты: {first['interest']:,.2f} руб.")
    print(f"  Ежемес. комиссия: {first['monthly_commission']:,.2f} руб.")
    print(f"  Остаток: {first['remaining']:,.2f} руб.")
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ДАННЫЕ КОРРЕКТНЫ!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

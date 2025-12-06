"""
Полный тест калькулятора через Django views
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_mvp.settings')
django.setup()

from django.test import RequestFactory
from finance.views import CalculatorView

# Создаем фабрику запросов
factory = RequestFactory()

# 1. Тест БЕЗ комиссий
print("=" * 60)
print("ТЕСТ 1: Калькулятор БЕЗ комиссий")
print("=" * 60)
post_data = {
    'amount': '100000',
    'months': '12',
    'rate': '15',
    'one_time_commission': '0',
    'monthly_commission': '0',
}
request = factory.post('/calculator/', data=post_data)
view = CalculatorView()
response = view.post(request)

print(f"Status: {response.status_code}")
if hasattr(response, 'context_data'):
    print(f"annuity_schedule exists: {'annuity_schedule' in response.context_data}")
    if 'annuity_schedule' in response.context_data:
        print(f"  Length: {len(response.context_data['annuity_schedule'])}")
        print(f"  Overpayment: {response.context_data.get('annuity_overpayment', 'N/A')}")
print()

# 2. Тест С комиссиями
print("=" * 60)
print("ТЕСТ 2: Калькулятор С комиссиями (2%, 1%)")
print("=" * 60)
post_data = {
    'amount': '100000',
    'months': '12',
    'rate': '15',
    'one_time_commission': '2',
    'monthly_commission': '1',
}
request = factory.post('/calculator/', data=post_data)
view = CalculatorView()
response = view.post(request)

print(f"Status: {response.status_code}")
if hasattr(response, 'context_data'):
    print(f"annuity_schedule exists: {'annuity_schedule' in response.context_data}")
    if 'annuity_schedule' in response.context_data:
        print(f"  Length: {len(response.context_data['annuity_schedule'])}")
        print(f"  Overpayment: {response.context_data.get('annuity_overpayment', 'N/A')}")
        print(f"✅ КАЛЬКУЛЯТОР РАБОТАЕТ С КОМИССИЯМИ!")
    else:
        print(f"❌ annuity_schedule НЕ В КОНТЕКСТЕ")
        print(f"Ключи контекста: {list(response.context_data.keys()) if hasattr(response, 'context_data') else 'нет context_data'}")
else:
    print("❌ Нет context_data в ответе")
    print(f"Response type: {type(response)}")

print("\n" + "=" * 60)
print("ВЫВОД: Если оба теста показали annuity_schedule - всё работает!")
print("=" * 60)

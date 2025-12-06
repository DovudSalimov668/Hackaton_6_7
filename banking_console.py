"""
Консольное приложение Banking MVP для Eskhata
Включает 3 финансовых инструмента с matplotlib визуализацией
"""
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Backend для Windows

# Добавляем путь к Django проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_mvp.settings')

import django
django.setup()

from finance.services import (
    calculate_annuity_loan,
    calculate_differentiated_loan,
    convert_currency,
    get_currency_forecast,
    get_currency_history
)
from finance.models import PaymentSchedule


def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Печать заголовка"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def get_input(prompt, input_type=str, min_val=None, max_val=None):
    """Безопасный ввод с валидацией"""
    while True:
        try:
            value = input(prompt)
            if value.lower() == 'q':
                return None
            
            if input_type == int:
                value = int(value)
            elif input_type == float:
                value = float(value)
            
            if min_val is not None and value < min_val:
                print(f"❌ Значение должно быть >= {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"❌ Значение должно быть <= {max_val}")
                continue
                
            return value
        except ValueError:
            print(f"❌ Неверный формат. Ожидается {input_type.__name__}")
        except KeyboardInterrupt:
            return None


def loan_calculator():
    """Кейс 1: Кредитный калькулятор с графиками"""
    clear_screen()
    print_header("🧮 КРЕДИТНЫЙ КАЛЬКУЛЯТОР")
    
    # Ввод параметров
    amount = get_input("Сумма кредита (100-500000 руб.): ", float, 100, 500000)
    if amount is None:
        return
    
    months = get_input("Срок (1-120 месяцев): ", int, 1, 120)
    if months is None:
        return
    
    rate = get_input("Процентная ставка (1-35% годовых): ", float, 1, 35)
    if rate is None:
        return
    
    one_time = get_input("Единовременная комиссия (0-5%): ", float, 0, 5)
    if one_time is None:
        one_time = 0
    
    monthly = get_input("Ежемесячная комиссия (0-2%): ", float, 0, 2)
    if monthly is None:
        monthly = 0
    
    print("\n⏳ Расчет...")
    
    # Расчет графиков
    annuity, ann_commission = calculate_annuity_loan(amount, months, rate, one_time, monthly)
    diff, diff_commission = calculate_differentiated_loan(amount, months, rate, one_time, monthly)
    
    # Статистика
    ann_total = sum(p['payment'] for p in annuity) + ann_commission
    ann_interest = sum(p['interest'] for p in annuity)
    ann_monthly_comm = sum(p['monthly_commission'] for p in annuity)
    
    diff_total = sum(p['payment'] for p in diff) + diff_commission
    diff_interest = sum(p['interest'] for p in diff)
    diff_monthly_comm = sum(p['monthly_commission'] for p in diff)
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ РАСЧЕТА")
    print("=" * 60)
    
    print(f"\n📌 АННУИТЕТНЫЙ ГРАФИК:")
    print(f"   Ежемесячный платеж: {annuity[0]['payment']:,.2f} ₽ (фиксированный)")
    print(f"   Переплата по процентам: {ann_interest:,.2f} ₽")
    print(f"   Комиссии: {ann_commission + ann_monthly_comm:,.2f} ₽")
    print(f"   Общая сумма выплат: {ann_total:,.2f} ₽")
    
    print(f"\n📌 ДИФФЕРЕНЦИРОВАННЫЙ ГРАФИК:")
    print(f"   Первый платеж: {diff[0]['payment']:,.2f} ₽")
    print(f"   Последний платеж: {diff[-1]['payment']:,.2f} ₽")
    print(f"   Переплата по процентам: {diff_interest:,.2f} ₽")
    print(f"   Комиссии: {diff_commission + diff_monthly_comm:,.2f} ₽")
    print(f"   Общая сумма выплат: {diff_total:,.2f} ₽")
    
    print(f"\n💰 ЭКОНОМИЯ при выборе дифференцированного графика:")
    print(f"   {ann_total - diff_total:,.2f} ₽")
    
    # Визуализация
    show_graphs = input("\n📊 Показать графики? (y/n): ").lower() == 'y'
    if show_graphs:
        create_loan_charts(annuity, diff, amount, ann_interest, diff_interest, 
                          ann_commission + ann_monthly_comm)
    
    input("\n✅ Нажмите Enter для продолжения...")


def create_loan_charts(annuity, diff, amount, ann_interest, diff_interest, commissions):
    """Создание графиков для кредитного калькулятора"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Кредитный калькулятор - Анализ', fontsize=16, fontweight='bold')
    
    months = [p['month'] for p in annuity]
    
    # 1. Сравнение платежей
    ax1.plot(months, [p['payment'] for p in annuity], 'b-', label='Аннуитетный', linewidth=2)
    ax1.plot(months, [p['payment'] for p in diff], 'r-', label='Дифференцированный', linewidth=2)
    ax1.set_xlabel('Месяц')
    ax1.set_ylabel('Платеж (₽)')
    ax1.set_title('Сравнение ежемесячных платежей')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Остаток долга
    ax2.plot(months, [p['remaining'] for p in annuity], 'b-', label='Аннуитетный', linewidth=2)
    ax2.plot(months, [p['remaining'] for p in diff], 'r-', label='Дифференцированный', linewidth=2)
    ax2.set_xlabel('Месяц')
    ax2.set_ylabel('Остаток (₽)')
    ax2.set_title('Динамика остатка долга')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Pie Chart - структура переплаты
    labels = ['Тело кредита', 'Проценты', 'Комиссии']
    sizes = [amount, ann_interest, commissions]
    colors = ['#00a651', '#ef4444', '#ffa500']
    ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax3.set_title('Структура общих выплат (Аннуитет)')
    
    # 4. Stacked bar - платеж по месяцам
    width = 0.35
    x = range(min(12, len(months)))  # Показываем только первые 12 месяцев
    
    principal = [annuity[i]['principal'] for i in x]
    interest = [annuity[i]['interest'] for i in x]
    
    ax4.bar(x, principal, width, label='Тело долга', color='#00a651')
    ax4.bar(x, interest, width, bottom=principal, label='Проценты', color='#ef4444')
    ax4.set_xlabel('Месяц')
    ax4.set_ylabel('Сумма (₽)')
    ax4.set_title('Структура платежей (первые 12 мес.)')
    ax4.set_xticks(x)
    ax4.set_xticklabels([i+1 for i in x])
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()


def currency_converter():
    """Кейс 2: Валютный конвертер с прогнозом"""
    clear_screen()
    print_header("💱 ВАЛЮТНЫЙ КОНВЕРТЕР")
    
    # Выбор валюты
    print("Доступные валюты:")
    print("1. USD - Доллар США")
    print("2. EUR - Евро")
    
    choice = get_input("\nВыберите валюту (1-2): ", int, 1, 2)
    if choice is None:
        return
    
    currency = 'USD' if choice == 1 else 'EUR'
    
    # Сумма
    amount = get_input(f"Сумма в {currency}: ", float, 0.01)
    if amount is None:
        return
    
    # Операция
    print("\nОперация:")
    print("1. Купить валюту (банк продает)")
    print("2. Продать валюту (банк покупает)")
    
    op_choice = get_input("Выбор (1-2): ", int, 1, 2)
    if op_choice is None:
        return
    
    operation = 'buy' if op_choice == 1 else 'sell'
    
    # Конвертация
    result = convert_currency(amount, currency, operation)
    forecast = get_currency_forecast(currency, days=7)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ КОНВЕРТАЦИИ")
    print("=" * 60)
    print(f"\n{amount:,.2f} {currency} = {result['result']:,.2f} ₽")
    print(f"Курс: {result['rate']:,.4f} ₽")
    print(f"Операция: {result['explanation']}")
    
    if forecast:
        print("\n📈 ПРОГНОЗ НА ЗАВТРА (средний за 7 дней):")
        print(f"   Покупка: {forecast['buy_forecast']:,.4f} ₽")
        print(f"   Продажа: {forecast['sell_forecast']:,.4f} ₽")
    
    # График
    show_graph = input("\n📊 Показать график истории? (y/n): ").lower() == 'y'
    if show_graph:
        create_currency_chart(currency)
    
    input("\n✅ Нажмите Enter для продолжения...")


def create_currency_chart(currency):
    """График истории курсов валюты"""
    history = get_currency_history(currency, days=180)
    
    plt.figure(figsize=(12, 6))
    plt.plot(history['labels'], history['buy_data'], 'g-', label='Курс покупки', linewidth=2)
    plt.plot(history['labels'], history['sell_data'], 'r-', label='Курс продажи', linewidth=2)
    
    plt.xlabel('Дата')
    plt.ylabel('Курс (₽)')
    plt.title(f'История курса {currency} (180 дней)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def payment_reminders():
    """Кейс 3: Напоминания о платежах"""
    clear_screen()
    print_header("📅 НАПОМИНАНИЯ О ПЛАТЕЖАХ")
    
    today = date.today()
    
    # Получаем все платежи
    all_payments = PaymentSchedule.objects.all().order_by('due_date')
    
    if not all_payments:
        print("❌ Нет данных о платежах")
        print("\nЗапустите: python manage.py setup_test_data")
        input("\n✅ Нажмите Enter для продолжения...")
        return
    
    # Ближайший платеж
    upcoming = all_payments.filter(due_date__gte=today, is_paid=False).first()
    
    # Просроченные
    overdue = all_payments.filter(
        due_date__lt=today,
        is_paid=False
    )
    
    print(f"📆 Сегодня: {today.strftime('%d.%m.%Y')}\n")
    
    # Ближайший платеж
    if upcoming:
        days_until = (upcoming.due_date - today).days
        print("🔔 БЛИЖАЙШИЙ ПЛАТЕЖ:")
        print(f"   Дата: {upcoming.due_date.strftime('%d.%m.%Y')} ({days_until} дн.)")
        print(f"   Сумма: {upcoming.planned_amount:,.2f} ₽")
        print(f"   Описание: {upcoming.description}")
        
        if days_until == 0:
            print("\n   🚨 СЕГОДНЯ! Не забудьте оплатить!")
        elif days_until == 1:
            print("\n   ⚠️  ЗАВТРА! Подготовьте средства!")
    else:
        print("✅ Нет предстоящих платежей\n")
    
    # Просрочки
    if overdue.exists():
        total_debt = sum(p.planned_amount - p.paid_amount for p in overdue)
        print(f"\n❌ ПРОСРОЧЕННЫЕ ПЛАТЕЖИ: {overdue.count()} шт.")
        print(f"   Общая сумма долга: {total_debt:,.2f} ₽")
        print("\n   Список:")
        for payment in overdue[:5]:  # Показываем первые 5
            debt = payment.planned_amount - payment.paid_amount
            days_overdue = (today - payment.due_date).days
            print(f"   • {payment.due_date.strftime('%d.%m.%Y')} - {debt:,.2f} ₽ (просрочка {days_overdue} дн.)")
    else:
        print("\n✅ Просрочек нет!")
    
    # Таблица всех платежей
    print("\n" + "=" * 80)
    print(f"{'Дата':<12} {'Описание':<30} {'Сумма':<15} {'Статус':<15}")
    print("=" * 80)
    
    for payment in all_payments[:12]:  # Показываем 12 платежей
        status =  "✅ Оплачено" if payment.is_paid else ("❌ Просрочка" if payment.due_date < today else "⏳ Ожидается")
        print(f"{payment.due_date.strftime('%d.%m.%Y'):<12} "
              f"{payment.description[:28]:<30} "
              f"{payment.planned_amount:>12,.2f} ₽  "
              f"{status:<15}")
    
    input("\n✅ Нажмите Enter для продолжения...")


def main_menu():
    """Главное меню"""
    while True:
        clear_screen()
        print_header("🏦 ESKHATA BANK - Консольное приложение")
        
        print("Выберите инструмент:\n")
        print("1. 🧮 Кредитный калькулятор")
        print("2. 💱 Валютный конвертер")
        print("3. 📅 Напоминания о платежах")
        print("\n0. ❌ Выход")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == '1':
            loan_calculator()
        elif choice == '2':
            currency_converter()
        elif choice == '3':
            payment_reminders()
        elif choice == '0':
            print("\n👋 До свидания!")
            break
        else:
            print("\n❌ Неверный выбор!")
            input("Нажмите Enter...")


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

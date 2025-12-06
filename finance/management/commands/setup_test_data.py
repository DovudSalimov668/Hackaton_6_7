"""
Management команда для генерации тестовых данных
Запуск: python manage.py setup_test_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from finance.models import Transaction, PaymentSchedule, CurrencyRate


class Command(BaseCommand):
    help = 'Генерация тестовых данных для демонстрации банковского приложения'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем генерацию тестовых данных...'))
        
        # Очистка старых данных
        Transaction.objects.all().delete()
        PaymentSchedule.objects.all().delete()
        CurrencyRate.objects.all().delete()
        self.stdout.write('Старые данные удалены')
        
        # Генерация транзакций
        self.generate_transactions()
        
        # Генерация графика платежей
        self.generate_payment_schedule()
        
        # Генерация курсов валют
        self.generate_currency_rates()
        
        self.stdout.write(self.style.SUCCESS('✅ Тестовые данные успешно созданы!'))
    
    def generate_transactions(self):
        """Генерация 50 случайных транзакций за последние 30 дней"""
        categories = ['Food', 'Transport', 'Communication', 'Entertainment', 'Shopping', 'Bills', 'Other']
        
        descriptions = {
            'Food': ['Продуктовый магазин', 'Ресторан', 'Кафе', 'Доставка еды', 'Пекарня'],
            'Transport': ['Заправка', 'Такси', 'Метро', 'Автобус', 'Парковка'],
            'Communication': ['Мобильная связь', 'Интернет', 'ТВ подписка'],
            'Entertainment': ['Кино', 'Театр', 'Концерт', 'Игры', 'Спортзал'],
            'Shopping': ['Одежда', 'Обувь', 'Электроника', 'Книги', 'Аптека'],
            'Bills': ['Коммунальные услуги', 'Электричество', 'Вода', 'ЖКХ'],
            'Other': ['Разное', 'Подарки', 'Прочие расходы', 'Услуги']
        }
        
        amount_ranges = {
            'Food': (200, 3000),
            'Transport': (100, 2000),
            'Communication': (300, 1500),
            'Entertainment': (500, 5000),
            'Shopping': (1000, 15000),
            'Bills': (2000, 8000),
            'Other': (500, 5000)
        }
        
        today = date.today()
        transactions = []
        
        for i in range(50):
            category = random.choice(categories)
            days_ago = random.randint(0, 30)
            transaction_date = today - timedelta(days=days_ago)
            
            min_amount, max_amount = amount_ranges[category]
            amount = Decimal(random.uniform(min_amount, max_amount)).quantize(Decimal('0.01'))
            
            description = random.choice(descriptions[category])
            
            transactions.append(Transaction(
                date=transaction_date,
                amount=amount,
                category=category,
                description=description
            ))
        
        Transaction.objects.bulk_create(transactions)
        self.stdout.write(f'✓ Создано {len(transactions)} транзакций')
    
    def generate_payment_schedule(self):
        """Генерация графика платежей на 12 месяцев"""
        today = date.today()
        payments = []
        
        # Начинаем с 3 месяца назад
        start_date = today - timedelta(days=90)
        
        for month in range(12):
            payment_date = start_date + timedelta(days=30 * month)
            planned_amount = Decimal(random.uniform(10000, 20000)).quantize(Decimal('0.01'))
            
            # Определяем статус платежа
            if payment_date < today - timedelta(days=30):
                # Старые платежи - оплачены
                is_paid = True
                paid_amount = planned_amount
                paid_date = payment_date
            elif payment_date < today:
                # Просроченные платежи (2 штуки)
                is_paid = False
                paid_amount = Decimal('0')
                paid_date = None
            elif payment_date == today + timedelta(days=1):
                # Платеж на завтра (для желтого алерта)
                is_paid = False
                paid_amount = Decimal('0')
                paid_date = None
            else:
                # Будущие платежи
                is_paid = False
                paid_amount = Decimal('0')
                paid_date = None
            
            payments.append(PaymentSchedule(
                due_date=payment_date,
                planned_amount=planned_amount,
                description=f'Платеж по кредиту #{month + 1}',
                is_paid=is_paid,
                paid_amount=paid_amount,
                paid_date=paid_date
            ))
        
        PaymentSchedule.objects.bulk_create(payments)
        self.stdout.write(f'✓ Создан график платежей на {len(payments)} месяцев')
    
    def generate_currency_rates(self):
        """Генерация истории курсов валют за 180 дней с реалистичным трендом"""
        today = date.today()
        days = 180
        
        # Базовые курсы
        usd_base = 90.0
        eur_base = 100.0
        spread = 2.0  # Разница между покупкой и продажей
        
        rates = []
        
        for i in range(days, -1, -1):
            rate_date = today - timedelta(days=i)
            
            # Генерация реалистичного тренда с волатильностью
            # Используем синусоиду + случайный шум для имитации рынка
            trend = random.uniform(-0.5, 0.5)  # Тренд
            volatility = random.uniform(-2, 2)  # Волатильность
            seasonal = 3 * (1 + 0.5 * (i / days))  # Сезонность
            
            # USD
            usd_mid = usd_base + trend * i / 10 + volatility + seasonal
            usd_buy = Decimal(usd_mid).quantize(Decimal('0.0001'))
            usd_sell = Decimal(usd_mid + spread).quantize(Decimal('0.0001'))
            
            rates.append(CurrencyRate(
                date=rate_date,
                currency_code='USD',
                buy_rate=usd_buy,
                sell_rate=usd_sell
            ))
            
            # EUR
            eur_mid = eur_base + trend * i / 10 + volatility * 1.2 + seasonal * 1.1
            eur_buy = Decimal(eur_mid).quantize(Decimal('0.0001'))
            eur_sell = Decimal(eur_mid + spread).quantize(Decimal('0.0001'))
            
            rates.append(CurrencyRate(
                date=rate_date,
                currency_code='EUR',
                buy_rate=eur_buy,
                sell_rate=eur_sell
            ))
        
        CurrencyRate.objects.bulk_create(rates)
        self.stdout.write(f'✓ Создана история курсов валют за {days + 1} дней')

from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """Модель транзакций для анализа расходов (Кейс 4)"""
    
    CATEGORY_CHOICES = [
        ('Food', 'Еда'),
        ('Transport', 'Транспорт'),
        ('Communication', 'Связь'),
        ('Entertainment', 'Развлечения'),
        ('Shopping', 'Покупки'),
        ('Bills', 'Коммунальные услуги'),
        ('Other', 'Прочее'),
    ]
    
    date = models.DateField('Дата транзакции', default=timezone.now)
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField('Описание', max_length=200)
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.get_category_display()}: {self.amount} руб."


class PaymentSchedule(models.Model):
    """Модель графика платежей для напоминаний (Кейс 5)"""
    
    due_date = models.DateField('Дата платежа')
    planned_amount = models.DecimalField('Запланированная сумма', max_digits=10, decimal_places=2)
    description = models.CharField('Описание платежа', max_length=200, default='Платеж по кредиту')
    is_paid = models.BooleanField('Оплачено', default=False)
    paid_amount = models.DecimalField('Оплаченная сумма', max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateField('Дата оплаты', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'График платежей'
        ordering = ['due_date']
    
    def __str__(self):
        status = "Оплачено" if self.is_paid else "Не оплачено"
        return f"{self.due_date} - {self.planned_amount} руб. ({status})"
    
    @property
    def is_overdue(self):
        """Проверка просрочки платежа"""
        from datetime import date
        today = date.today()
        return today > self.due_date and self.paid_amount < self.planned_amount
    
    @property
    def debt_amount(self):
        """Сумма задолженности"""
        return max(0, self.planned_amount - self.paid_amount)


class CurrencyRate(models.Model):
    """Модель курсов валют (Кейс 7)"""
    
    CURRENCY_CHOICES = [
        ('USD', 'Доллар США'),
        ('EUR', 'Евро'),
    ]
    
    date = models.DateField('Дата')
    currency_code = models.CharField('Код валюты', max_length=3, choices=CURRENCY_CHOICES)
    buy_rate = models.DecimalField('Курс покупки', max_digits=10, decimal_places=4)
    sell_rate = models.DecimalField('Курс продажи', max_digits=10, decimal_places=4)
    
    class Meta:
        verbose_name = 'Курс валюты'
        verbose_name_plural = 'Курсы валют'
        ordering = ['-date']
        unique_together = ['date', 'currency_code']
    
    def __str__(self):
        return f"{self.date} - {self.get_currency_code_display()}: {self.buy_rate}/{self.sell_rate}"

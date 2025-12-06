
import os
"""
Патч для views.py чтобы гарантировать работу CurrencyView
"""
original_file = 'finance/views.py'

new_view_code = """
class CurrencyView(TemplateView):
    \"\"\"Кейс 7: Обмен валют\"\"\"
    template_name = 'currency.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Значения по умолчанию
        context['amount'] = 100
        context['currency'] = 'USD'
        context['operation'] = 'buy'
        context['history_days'] = 30
        
        try:
            # Прогноз курса USD
            usd_forecast = services.get_currency_forecast('USD', days=7)
            context['usd_forecast'] = usd_forecast if usd_forecast else {}
            
            # Прогноз курса EUR
            eur_forecast = services.get_currency_forecast('EUR', days=7)
            context['eur_forecast'] = eur_forecast if eur_forecast else {}
            
            # История курсов для графика
            # Всегда возвращаем валидный JSON, даже если данных нет
            
            # USD
            try:
                usd_hist_data = services.get_currency_history('USD', days=30)
                if not usd_hist_data or not usd_hist_data.get('labels'):
                    usd_hist_data = {'labels': [], 'buy_data': [], 'sell_data': []}
            except Exception:
                usd_hist_data = {'labels': [], 'buy_data': [], 'sell_data': []}
                
            context['usd_history'] = json.dumps(usd_hist_data, ensure_ascii=False)
            
            # EUR
            try:
                eur_hist_data = services.get_currency_history('EUR', days=30)
                if not eur_hist_data or not eur_hist_data.get('labels'):
                    eur_hist_data = {'labels': [], 'buy_data': [], 'sell_data': []}
            except Exception:
                eur_hist_data = {'labels': [], 'buy_data': [], 'sell_data': []}
                
            context['eur_history'] = json.dumps(eur_hist_data, ensure_ascii=False)

        except Exception as e:
            print(f"Error in CurrencyView context: {e}")
            # Fallback values
            context['usd_forecast'] = {}
            context['eur_forecast'] = {}
            context['usd_history'] = '{}'
            context['eur_history'] = '{}'
        
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
            try:
                conversion = services.convert_currency(amount, currency, operation)
                context['conversion'] = conversion
            except Exception as e:
                context['error'] = f'Ошибка конвертации: {str(e)}'
            
        except (ValueError, TypeError) as e:
            context['error'] = 'Ошибка в параметрах конвертации'
        
        return render(request, self.template_name, context)
"""

# Читаем файл
with open(original_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Находим начало класса CurrencyView
start_marker = "class CurrencyView"
end_marker = "class PaymentsView"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_view_code + "\n\n" + content[end_idx:]
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ CurrencyView successfully replaced with safe version")
else:
    print("❌ Could not find CurrencyView class boundaries")

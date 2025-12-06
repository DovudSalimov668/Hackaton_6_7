import re

# Чтение файла
with open('finance/templates/currency.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Замена операторов ==
content = re.sub(r"currency=='USD'", "currency == 'USD'", content)
content = re.sub(r"currency=='EUR'", "currency == 'EUR'", content)  
content = re.sub(r"operation=='buy'", "operation == 'buy'", content)
content = re.sub(r"operation=='sell'", "operation == 'sell'", content)
content = re.sub(r"history_days==30", "history_days == 30", content)
content = re.sub(r"history_days==60", "history_days == 60", content)
content = re.sub(r"history_days==180", "history_days == 180", content)

# Запись обратно
with open('finance/templates/currency.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all template syntax in currency.html")

# Script to replace analyze_expenses function
content = open('finance/services.py', 'r', encoding='utf-8').read()

new_function = '''def analyze_expenses():
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
    }'''

# Find and replace
start = content.find('def analyze_expenses():')
end = content.find('\n\n# ====', start)
new_content = content[:start] + new_function + content[end:]

# Write back
with open('finance/services.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ analyze_expenses function updated!")

"""
CSV Data Loader для консольного приложения
Загружает mock данные из CSV файлов
"""
import csv
import os
from datetime import datetime
from decimal import Decimal


class CSVDataLoader:
    """Загрузчик данных из CSV файлов"""
    
    def __init__(self, data_dir='mock_data'):
        """
        Args:
            data_dir: директория с CSV файлами
        """
        self.data_dir = data_dir
        
    def load_transactions(self, filename='transactions.csv'):
        """
        Загружает транзакции из CSV
        
        Returns:
            list: список словарей с транзакциями
        """
        filepath = os.path.join(self.data_dir, filename)
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    transactions.append({
                        'id': int(row['transaction_id']),
                        'date': datetime.strptime(row['transaction_date'], '%d/%m/%Y %H:%M:%S'),
                        'amount': float(row['amount']),
                        'currency': row['currency_code'],
                        'description': row['description'],
                        'category_id': int(row['category_id']) if row['category_id'] else None,
                        'is_cancelled': row['is_cancelled'].lower() == 't'
                    })
            print(f"✅ Загружено {len(transactions)} транзакций из {filename}")
            return transactions
        except FileNotFoundError:
            print(f"❌ Файл {filepath} не найден")
            return []
        except Exception as e:
            print(f"❌ Ошибка при загрузке транзакций: {e}")
            return []
    
    def load_categories(self, filename='transaction_categories.csv'):
        """
        Загружает категории транзакций
        
        Returns:
            dict: словарь {id: category_info}
        """
        filepath = os.path.join(self.data_dir, filename)
        categories = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cat_id = int(row['category_id'])
                    categories[cat_id] = {
                        'id': cat_id,
                        'name': row['category_name'],
                        'description': row['description'],
                        'is_expense': row['is_expense'].lower() == 't',
                        'parent_id': int(row['parent_category_id']) if row['parent_category_id'] else None
                    }
            print(f"✅ Загружено {len(categories)} категорий из {filename}")
            return categories
        except FileNotFoundError:
            print(f"❌ Файл {filepath} не найден")
            return {}
        except Exception as e:
            print(f"❌ Ошибка при загрузке категорий: {e}")
            return {}
    
    def load_currencies(self, filename='currencies.csv'):
        """
        Загружает справочник валют
        
        Returns:
            dict: словарь {code: currency_info}
        """
        filepath = os.path.join(self.data_dir, filename)
        currencies = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row['currency_code']
                    currencies[code] = {
                        'code': code,
                        'name': row['currency_name'],
                        'symbol': row['symbol']
                    }
            print(f"✅ Загружено {len(currencies)} валют из {filename}")
            return currencies
        except FileNotFoundError:
            print(f"❌ Файл {filepath} не найден")
            return {}
        except Exception as e:
            print(f"❌ Ошибка при загрузке валют: {e}")
            return {}
    
    def get_expenses(self, transactions, categories):
        """Возвращает только расходы (is_expense=True)"""
        expense_cat_ids = [cid for cid, cat in categories.items() if cat['is_expense']]
        return [t for t in transactions if t['category_id'] in expense_cat_ids and not t['is_cancelled']]
    
    def get_income(self, transactions, categories):
        """Возвращает только доходы (is_expense=False)"""
        income_cat_ids = [cid for cid, cat in categories.items() if not cat['is_expense']]
        return [t for t in transactions if t['category_id'] in income_cat_ids and not t['is_cancelled']]
    
    def calculate_category_totals(self, transactions, categories):
        """
        Подсчитывает общие суммы по категориям
        
        Returns:
            dict: {category_id: total_amount}
        """
        totals = {}
        for transaction in transactions:
            if transaction['is_cancelled']:
                continue
            
            cat_id = transaction['category_id']
            if cat_id:
                if cat_id not in totals:
                    totals[cat_id] = 0
                totals[cat_id] += transaction['amount']
        
        return totals


# Пример использования
if __name__ == '__main__':
    loader = CSVDataLoader()
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАГРУЗКИ CSV ДАННЫХ")
    print("=" * 60 + "\n")
    
    # Загрузка данных
    categories = loader.load_categories()
    currencies = loader.load_currencies()
    transactions = loader.load_transactions()
    
    if transactions and categories:
        # Анализ расходов
        expenses = loader.get_expenses(transactions, categories)
        income = loader.get_income(transactions, categories)
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"  Всего транзакций: {len(transactions)}")
        print(f"  Расходов: {len(expenses)}")
        print(f"  Доходов: {len(income)}")
        
        # Топ категории расходов
        expense_totals = {}
        for exp in expenses:
            cat_id = exp['category_id']
            if cat_id not in expense_totals:
                expense_totals[cat_id] = 0
            expense_totals[cat_id] += exp['amount']
        
        print(f"\n💰 ТОП-5 КАТЕГОРИЙ РАСХОДОВ:")
        sorted_expenses = sorted(expense_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        for cat_id, total in sorted_expenses:
            cat_name = categories[cat_id]['name']
            print(f"  {cat_name}: {total:,.2f}")

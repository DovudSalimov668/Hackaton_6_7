"""
Кейс 4: Анализ расходов клиентов
Загрузка CSV, классификация, подсчёт долей, визуализация
"""
import csv
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


class ExpenseAnalyzer:
    """Анализатор расходов клиентов банка"""
    
    def __init__(self, data_dir='mock_data'):
        self.data_dir = data_dir
        self.transactions = []
        self.categories = {}
        self.expenses = []
        
    def load_categories(self, filename='transaction_categories.csv'):
        """Загрузка справочника категорий"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cat_id = int(row['category_id'])
                    self.categories[cat_id] = {
                        'id': cat_id,
                        'name': row['category_name'],
                        'description': row['description'],
                        'is_expense': row['is_expense'].lower() == 't',
                        'parent_id': int(row['parent_category_id']) if row['parent_category_id'] else None
                    }
            print(f"✅ Загружено {len(self.categories)} категорий")
            return True
        except FileNotFoundError:
            print(f"❌ Файл {filepath} не найден")
            return False
        except Exception as e:
            print(f"❌ Ошибка загрузки категорий: {e}")
            return False
    
    def load_transactions(self, filename='transactions.csv'):
        """Загрузка транзакций из CSV"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.transactions.append({
                        'id': int(row['transaction_id']),
                        'date': datetime.strptime(row['transaction_date'], '%d/%m/%Y %H:%M:%S'),
                        'amount': float(row['amount']),
                        'currency': row['currency_code'],
                        'description': row['description'],
                        'category_id': int(row['category_id']) if row['category_id'] else None,
                        'is_cancelled': row['is_cancelled'].lower() == 't'
                    })
            print(f"✅ Загружено {len(self.transactions)} транзакций")
            return True
        except FileNotFoundError:
            print(f"❌ Файл {filepath} не найден")
            return False
        except Exception as e:
            print(f"❌ Ошибка загрузки транзакций: {e}")
            return False
    
    def classify_expenses(self):
        """Классификация расходов (только is_expense=True и не отменённые)"""
        expense_cat_ids = [cid for cid, cat in self.categories.items() if cat['is_expense']]
        
        self.expenses = [
            t for t in self.transactions 
            if t['category_id'] in expense_cat_ids and not t['is_cancelled']
        ]
        
        print(f"✅ Найдено {len(self.expenses)} расходов")
        return self.expenses
    
    def calculate_totals(self):
        """
        Подсчёт общих сумм и долей по категориям
        
        Returns:
            dict: {
                'total': общая сумма,
                'by_category': {category_id: {'sum': X, 'percent': Y, 'count': Z, 'name': ...}}
            }
        """
        total_amount = sum(exp['amount'] for exp in self.expenses)
        
        category_stats = defaultdict(lambda: {'sum': 0, 'count': 0})
        
        for expense in self.expenses:
            cat_id = expense['category_id']
            category_stats[cat_id]['sum'] += expense['amount']
            category_stats[cat_id]['count'] += 1
        
        # Добавляем проценты и названия
        result = {'total': total_amount, 'by_category': {}}
        
        for cat_id, stats in category_stats.items():
            cat_name = self.categories[cat_id]['name']
            percent = (stats['sum'] / total_amount * 100) if total_amount > 0 else 0
            
            result['by_category'][cat_id] = {
                'name': cat_name,
                'sum': stats['sum'],
                'count': stats['count'],
                'percent': percent,
                'avg': stats['sum'] / stats['count'] if stats['count'] > 0 else 0
            }
        
        return result
    
    def print_text_report(self, stats):
        """Текстовая визуализация - таблица"""
        print("\n" + "=" * 80)
        print("ОТЧЁТ ПО РАСХОДАМ КЛИЕНТА")
        print("=" * 80)
        
        print(f"\n💰 ОБЩАЯ СУММА РАСХОДОВ: {stats['total']:,.2f} руб.")
        print(f"📊 КОЛИЧЕСТВО КАТЕГОРИЙ: {len(stats['by_category'])}")
        print(f"📝 КОЛИЧЕСТВО ОПЕРАЦИЙ: {len(self.expenses)}")
        
        print("\n" + "-" * 80)
        print(f"{'№':<4} {'КАТЕГОРИЯ':<30} {'СУММА (руб.)':<18} {'КОЛ-ВО':<8} {'ДОЛЯ %':<10}")
        print("-" * 80)
        
        # Сортируем по сумме (от большего к меньшему)
        sorted_cats = sorted(
            stats['by_category'].items(), 
            key=lambda x: x[1]['sum'], 
            reverse=True
        )
        
        for idx, (cat_id, data) in enumerate(sorted_cats, 1):
            print(f"{idx:<4} {data['name']:<30} {data['sum']:>16,.2f}  {data['count']:<8} {data['percent']:>8.1f}%")
        
        print("-" * 80)
        
        # Топ-3 категории
        print("\n🔝 ТОП-3 КАТЕГОРИИ РАСХОДОВ:")
        for idx, (cat_id, data) in enumerate(sorted_cats[:3], 1):
            print(f"   {idx}. {data['name']}: {data['sum']:,.2f} руб. ({data['percent']:.1f}%)")
    
    def visualize_pie_chart(self, stats):
        """Круговая диаграмма (Pie Chart)"""
        # Берём топ-10 категорий
        sorted_cats = sorted(
            stats['by_category'].items(), 
            key=lambda x: x[1]['sum'], 
            reverse=True
        )[:10]
        
        labels = [data['name'] for _, data in sorted_cats]
        sizes = [data['sum'] for _, data in sorted_cats]
        colors = plt.cm.Set3(range(len(labels)))
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        # Улучшаем читаемость
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Доли расходов по категориям (ТОП-10)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def visualize_bar_chart(self, stats):
        """Столбчатая диаграмма"""
        # Берём топ-10 категорий
        sorted_cats = sorted(
            stats['by_category'].items(), 
            key=lambda x: x[1]['sum'], 
            reverse=True
        )[:10]
        
        labels = [data['name'] for _, data in sorted_cats]
        amounts = [data['sum'] for _, data in sorted_cats]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars = ax.bar(range(len(labels)), amounts, color='#007bff', alpha=0.8)
        
        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'{height:,.0f}',
                ha='center', 
                va='bottom',
                fontsize=9
            )
        
        ax.set_xlabel('Категории', fontsize=12)
        ax.set_ylabel('Сумма (руб.)', fontsize=12)
        ax.set_title('Расходы по категориям (ТОП-10)', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.yaxis.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_and_report(self):
        """Полный цикл анализа и отчётности"""
        print("\n" + "🏦 АНАЛИЗ РАСХОДОВ КЛИЕНТА БАНКА ".center(80, "="))
        
        # 1. Загрузка данных
        print("\n📂 ШАГ 1: Загрузка данных")
        if not self.load_categories():
            return False
        if not self.load_transactions():
            return False
        
        # 2. Классификация
        print("\n🔍 ШАГ 2: Классификация расходов")
        self.classify_expenses()
        
        if not self.expenses:
            print("❌ Нет расходов для анализа")
            return False
        
        # 3. Подсчёт долей
        print("\n🧮 ШАГ 3: Подсчёт сумм и долей")
        stats = self.calculate_totals()
        
        # 4. Визуализация
        print("\n📊 ШАГ 4: Визуализация")
        self.print_text_report(stats)
        
        # Спрашиваем про графики
        show_charts = input("\n📈 Показать графики? (y/n): ").lower() == 'y'
        
        if show_charts:
            print("\n🥧 Круговая диаграмма...")
            self.visualize_pie_chart(stats)
            
            print("\n📊 Столбчатая диаграмма...")
            self.visualize_bar_chart(stats)
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЁН!")
        print("=" * 80 + "\n")
        
        return True


def main():
    """Главная функция"""
    analyzer = ExpenseAnalyzer()
    
    result = analyzer.analyze_and_report()
    
    if result:
        print("\n💡 РЕКОМЕНДАЦИИ ДЛЯ БАНКА:")
        print("   На основе этих данных банк может:")
        print("   • Предложить кешбэк по популярным категориям")
        print("   • Рекомендовать специальные карты (например, для путешествий)")
        print("   • Создать персонализированные предложения")
        print("   • Помочь клиенту с бюджетированием")


if __name__ == '__main__':
    main()

# Fix all template Django template syntax errors
import re

files_to_fix = [
    'finance/templates/expenses.html',
    'finance/templates/calculator.html',
    'finance/templates/currency.html'
]

for filepath in files_to_fix:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix pattern: {{ variable| safe\n    }}; → {{ variable|safe }};
        # Remove spaces before |safe and fix line breaks
        
        # Pattern 1: Multi-line with space before |
        content = re.sub(
            r'\{\{\s*([^}]+?)\s*\|\s*safe\s*\n\s*\}\}',
            r'{{ \1|safe }}',
            content
        )
        
        # Pattern 2: Remove extra space before |safe on single line
        content = re.sub(
            r'\{\{\s*([^}]+?)\s*\|\s*safe\s*\}\}',
            r'{{ \1|safe }}',
            content
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {filepath}")
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

print("\n✅ All templates fixed!")

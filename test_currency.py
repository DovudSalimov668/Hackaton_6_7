"""
Test currency conversion functionality
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_mvp.settings')
django.setup()

from finance import services

print("=" * 60)
print("CURRENCY CONVERSION TEST")
print("=" * 60)

# Test USD forecast
print("\n1. USD Forecast (7 days):")
usd_forecast = services.get_currency_forecast('USD', days=7)
if usd_forecast:
    print(f"   Buy forecast: {usd_forecast['buy_forecast']} руб.")
    print(f"   Sell forecast: {usd_forecast['sell_forecast']} руб.")
    print(f"   ✅ USD forecast works!")
else:
    print("   ❌ No USD forecast data")

# Test EUR forecast
print("\n2. EUR Forecast (7 days):")
eur_forecast = services.get_currency_forecast('EUR', days=7)
if eur_forecast:
    print(f"   Buy forecast: {eur_forecast['buy_forecast']} руб.")
    print(f"   Sell forecast: {eur_forecast['sell_forecast']} руб.")
    print(f"   ✅ EUR forecast works!")
else:
    print("   ❌ No EUR forecast data")

# Test currency conversion
print("\n3. Currency Conversion Test:")
print(f"   Converting 100 USD (buy)...")
conversion = services.convert_currency(100, 'USD', 'buy')
if conversion:
    print(f"   Amount: {conversion['amount']} {conversion['currency']}")
    print(f"   Rate: {conversion['rate']} руб.")
    print(f"   Result: {conversion['result']} руб.")
    print(f"   {conversion['explanation']}")
    print(f"   ✅ Conversion works!")
else:
    print("   ❌ Conversion failed - no data")

# Test history
print("\n4. Currency History Test:")
usd_history = services.get_currency_history('USD', days=30)
if usd_history and usd_history['labels']:
    print(f"   History records: {len(usd_history['labels'])} days")
    print(f"   First date: {usd_history['labels'][0]}")
    print(f"   Last date: {usd_history['labels'][-1]}")
    print(f"   ✅ History works!")
else:
    print("   ❌ No history data")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

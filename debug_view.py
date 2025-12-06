
import os
import sys
import django
from django.test import RequestFactory
from django.urls import reverse

sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_mvp.settings')
django.setup()

from finance.views import CurrencyView

print("Testing CurrencyView...")
try:
    factory = RequestFactory()
    request = factory.get('/currency/')
    view = CurrencyView.as_view()
    response = view(request)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Response content (abbreviated):")
        print(response.content[:500])
except Exception as e:
    print("EXCEPTION OCCURRED:")
    import traceback
    traceback.print_exc()

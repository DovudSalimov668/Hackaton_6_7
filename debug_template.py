
import os
import sys
import django
from django.test import Client

sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_mvp.settings')
django.setup()

print("Testing /currency/ page rendering...")
try:
    c = Client()
    response = c.get('/currency/')
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Response content (abbreviated):")
        # TemplateSyntaxError usually renders a debug page.
        # We need to find the exception part.
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        exception_value = soup.find('h1', class_='exception_value')
        if exception_value:
             print(f"Exception: {exception_value.text}")
        else:
             print(response.content[:1000])
except Exception as e:
    print(f"EXCEPTION: {e}")

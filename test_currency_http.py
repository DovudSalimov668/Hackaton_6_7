"""
Direct test of currency page
"""
import requests

print("Testing currency page...")

try:
    # GET request
    response = requests.get('http://localhost:8000/currency/')
    print(f"GET Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Page loads successfully")
        
        # Check if contains conversion result
        if 'Конвертер валют' in response.text:
            print("✅ Converter form found")
        if 'Прогноз курса' in response.text:
            print("✅ Forecast section found")
        if 'usdChart' in response.text:
            print("✅ USD chart found")
        if 'eurChart' in response.text:
            print("✅ EUR chart found")
            
        # Check for errors
        if 'error' in response.text.lower() or 'ошибка' in response.text.lower():
            print("⚠️ May contain error messages")
    else:
        print(f"❌ Page returned status {response.status_code}")
    
    # POST request to test conversion
    print("\nTesting conversion form...")
    data = {
        'amount': 100,
        'currency': 'USD',
        'operation': 'buy',
        'history_days': 30
    }
    
    # Get CSRF token first
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if csrf_token:
        data['csrfmiddlewaretoken'] = csrf_token['value']
        
        # Create session to maintain cookies
        session = requests.Session()
        session.get('http://localhost:8000/currency/')
        
        post_response = session.post('http://localhost:8000/currency/', data=data)
        print(f"POST Status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            if 'Результат' in post_response.text or 'результат' in post_response.text:
                print("✅ Conversion result displayed")
            else:
                print("⚠️ Conversion result may not be displayed")
        else:
            print(f"❌ POST failed with status {post_response.status_code}")
    else:
        print("❌ No CSRF token found")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTest complete!")

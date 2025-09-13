
import requests

auth_response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'email': 'demo@sofinance.com',
    'password': 'demo123'
})

print(f"Auth status: {auth_response.status_code}")
if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test inventory valuation endpoint
    response = requests.get('http://localhost:8000/api/v1/inventory/valuation/report', headers=headers)
    print(f'Inventory Valuation Status: {response.status_code}')
    if response.status_code != 200:
        print(f'Error: {response.text}')
else:
    print(f'Authentication error: {auth_response.text}')

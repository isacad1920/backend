import requests
import json

auth_response = requests.post('http://localhost:8000/api/v1/auth/token', json={
    'username': 'demo@sofinance.com',
    'password': 'demo123',
    'grant_type': 'password'
})

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test category creation to see response format
    response = requests.post('http://localhost:8000/api/v1/categories/', 
                           headers=headers,
                           json={'name': 'Debug Test Category', 'description': 'Debug test category description'})
    print(f'Category Create Status: {response.status_code}')
    print(f'Response: {json.dumps(response.json(), indent=2)}')

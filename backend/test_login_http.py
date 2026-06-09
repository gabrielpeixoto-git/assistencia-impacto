import requests
import json

try:
    r = requests.post('http://localhost:8000/api/auth/login', 
        json={'email': 'admin@assistenciaimpacto.com.br', 'senha': 'admin123'},
        timeout=30)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('ERRO:', str(e))

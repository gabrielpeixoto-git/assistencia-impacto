import requests

response = requests.post('http://localhost:8000/api/auth/login', json={'email':'admin@assistenciaimpacto.com.br','senha':'admin123'})
print('Status:', response.status_code)
print('Body:', response.text)

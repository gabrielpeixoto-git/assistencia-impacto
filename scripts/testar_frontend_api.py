import urllib.request
import json

# Obter token
req = urllib.request.Request(
    'http://localhost:8000/api/auth/login',
    data=json.dumps({'email': 'admin@assistenciaimpacto.com.br', 'senha': 'admin123'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    token = data['access_token']

headers = {'Authorization': f'Bearer {token}'}

# Testar GET /api/clientes (sem Content-Type para GET)
print("=== Testando GET /api/clientes ===")
req = urllib.request.Request('http://localhost:8000/api/clientes', headers=headers)
with urllib.request.urlopen(req) as response:
    clientes = json.loads(response.read().decode())
    print(f"Status: {response.status}")
    print(f"Quantidade de clientes: {len(clientes)}")
    if clientes:
        print("\nPrimeiro cliente (formato do backend):")
        print(json.dumps(clientes[0], indent=2, ensure_ascii=False))

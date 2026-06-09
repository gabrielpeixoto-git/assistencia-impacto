import urllib.request
import json
import random
from datetime import datetime, timedelta

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

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Buscar transações
print("Buscando transações...")
req = urllib.request.Request('http://localhost:8000/api/financeiro/transacoes', headers=headers)
with urllib.request.urlopen(req) as response:
    transacoes = json.loads(response.read().decode())
    print(f"Total de transações: {len(transacoes)}")

# Atualizar transações para status PAGO
print("\nAtualizando transações para status PAGO...")
for trans in transacoes:
    data_pagamento = datetime.now() - timedelta(days=random.randint(1, 20))
    update_data = {
        'status': 'pago',
        'data_pagamento': data_pagamento.isoformat()
    }
    
    req = urllib.request.Request(
        f'http://localhost:8000/api/financeiro/transacoes/{trans["id"]}',
        data=json.dumps(update_data).encode('utf-8'),
        headers=headers,
        method='PUT'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  ✓ {trans['descricao']} atualizada para PAGO")

print("\n✓ Transações atualizadas com sucesso")

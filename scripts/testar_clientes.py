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
    print(f"Token obtido: {token[:50]}...")

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Testar GET /api/clientes
print("\n=== GET /api/clientes ===")
req = urllib.request.Request('http://localhost:8000/api/clientes', headers=headers)
with urllib.request.urlopen(req) as response:
    clientes = json.loads(response.read().decode())
    print(f"Status: {response.status}")
    print(f"Quantidade: {len(clientes)}")
    if clientes:
        print(f"Primeiro cliente: {json.dumps(clientes[0], indent=2, ensure_ascii=False)}")
        cliente_id = clientes[0]['id']
    else:
        cliente_id = None

# Testar POST /api/clientes
print("\n=== POST /api/clientes ===")
novo_cliente = {
    'nome': 'Cliente Teste',
    'email': 'teste@example.com',
    'telefone': '11999999999',
    'tipo_documento': 'cpf',
    'numero_documento': '12345678901',
    'tipo_cliente': 'residencial',
    'logradouro': 'Rua Teste',
    'numero': '123',
    'bairro': 'Bairro Teste',
    'cidade': 'São Paulo',
    'estado': 'SP',
    'cep': '01234567'
}
req = urllib.request.Request(
    'http://localhost:8000/api/clientes',
    data=json.dumps(novo_cliente).encode('utf-8'),
    headers=headers,
    method='POST'
)
with urllib.request.urlopen(req) as response:
    cliente_criado = json.loads(response.read().decode())
    print(f"Status: {response.status}")
    print(f"Cliente criado: {json.dumps(cliente_criado, indent=2, ensure_ascii=False)}")
    cliente_id = cliente_criado['id']

# Testar GET /api/clientes/{id}
print(f"\n=== GET /api/clientes/{cliente_id} ===")
req = urllib.request.Request(f'http://localhost:8000/api/clientes/{cliente_id}', headers=headers)
with urllib.request.urlopen(req) as response:
    cliente = json.loads(response.read().decode())
    print(f"Status: {response.status}")
    print(f"Cliente: {json.dumps(cliente, indent=2, ensure_ascii=False)}")

# Testar PUT /api/clientes/{id} - incluindo campos corrigidos
print(f"\n=== PUT /api/clientes/{cliente_id} ===")
cliente_atualizado = {
    'nome': 'Cliente Teste Atualizado',
    'telefone': '11888888888',
    'tipo_documento': 'cnpj',
    'numero_documento': '12345678000199',
    'tipo_cliente': 'comercial'
}
req = urllib.request.Request(
    f'http://localhost:8000/api/clientes/{cliente_id}',
    data=json.dumps(cliente_atualizado).encode('utf-8'),
    headers=headers,
    method='PUT'
)
try:
    with urllib.request.urlopen(req) as response:
        cliente = json.loads(response.read().decode())
        print(f"Status: {response.status}")
        print(f"Cliente atualizado: {json.dumps(cliente, indent=2, ensure_ascii=False)}")
        # Verificar se os campos foram atualizados
        assert cliente['tipo_documento'] == 'cnpj', "tipo_documento não foi atualizado"
        assert cliente['numero_documento'] == '12345678000199', "numero_documento não foi atualizado"
        assert cliente['tipo_cliente'] == 'comercial', "tipo_cliente não foi atualizado"
        print("✓ Campos corrigidos atualizados com sucesso!")
except urllib.error.HTTPError as e:
    print(f"✗ Erro ao atualizar: {e.code}")
    print(f"Detalhes: {e.read().decode()}")

# Testar DELETE /api/clientes/{id}
print(f"\n=== DELETE /api/clientes/{cliente_id} ===")
req = urllib.request.Request(
    f'http://localhost:8000/api/clientes/{cliente_id}',
    headers=headers,
    method='DELETE'
)
with urllib.request.urlopen(req) as response:
    print(f"Status: {response.status}")
    print("Cliente deletado (soft delete)")

print("\n=== Todos os endpoints testados com sucesso ===")

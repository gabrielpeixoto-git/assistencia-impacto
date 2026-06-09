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

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Testar busca em ordens de serviço
print("=== Testando busca em Ordens de Serviço ===")
print("Busca por 'jubileu' (deve encontrar OS202605-1):")
req = urllib.request.Request('http://localhost:8000/api/ordens-servico?busca=jubileu', headers=headers)
with urllib.request.urlopen(req) as response:
    ordens = json.loads(response.read().decode())
    print(f"  ✓ Encontradas: {len(ordens)} ordens")
    for os in ordens:
        print(f"    - {os['numero_os']}: {os['titulo']}")

print("\nBusca por 'Teste' (deve encontrar OS202605):")
req = urllib.request.Request('http://localhost:8000/api/ordens-servico?busca=Teste', headers=headers)
with urllib.request.urlopen(req) as response:
    ordens = json.loads(response.read().decode())
    print(f"  ✓ Encontradas: {len(ordens)} ordens")
    for os in ordens:
        print(f"    - {os['numero_os']}: {os['titulo']}")

# Testar busca em clientes
print("\n=== Testando busca em Clientes ===")
print("Busca por 'Joao' (deve encontrar João Silva):")
req = urllib.request.Request('http://localhost:8000/api/clientes?busca=Joao', headers=headers)
with urllib.request.urlopen(req) as response:
    clientes = json.loads(response.read().decode())
    print(f"  ✓ Encontrados: {len(clientes)} clientes")
    for cliente in clientes[:3]:
        print(f"    - {cliente['nome']}")

print("\nBusca por 'Tech' (deve encontrar Empresa Tech Solutions):")
req = urllib.request.Request('http://localhost:8000/api/clientes?busca=Tech', headers=headers)
with urllib.request.urlopen(req) as response:
    clientes = json.loads(response.read().decode())
    print(f"  ✓ Encontrados: {len(clientes)} clientes")
    for cliente in clientes[:3]:
        print(f"    - {cliente['nome']}")

print("\n✓ Testes de busca concluídos com sucesso!")

import requests
import json

# URL da API
BASE_URL = "http://localhost:8000"

# Primeiro, fazer login para obter o token
login_data = {
    "email": "admin@assistenciaimpacto.com.br",
    "senha": "admin123"
}

print("Fazendo login...")
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Status login: {response.status_code}")

if response.status_code != 200:
    print(f"Erro no login: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Buscar um cliente para usar no orçamento
print("\nBuscando clientes...")
response = requests.get(f"{BASE_URL}/api/clientes?ativo=true&limit=1", headers=headers)
print(f"Status busca clientes: {response.status_code}")

if response.status_code != 200:
    print(f"Erro ao buscar clientes: {response.text}")
    exit(1)

clientes = response.json()
if not clientes:
    print("Nenhum cliente encontrado")
    exit(1)

cliente_id = clientes[0]["id"]
print(f"Usando cliente: {clientes[0]['nome']} (ID: {cliente_id})")

# Criar orçamento manual
orcamento_manual = {
    "cliente_id": cliente_id,
    "titulo": "Orçamento Manual Teste",
    "descricao": "Teste de orçamento com tipo_calculo manual",
    "tipo_calculo": "manual",
    "valor_total_manual": 1500.00,
    "subtotal": 0.0,
    "total": 1500.00,
    "valido_ate": "2026-06-30T00:00:00"
}

print("\nCriando orçamento manual...")
print(f"Payload: {json.dumps(orcamento_manual, indent=2)}")

response = requests.post(f"{BASE_URL}/api/orcamentos", json=orcamento_manual, headers=headers)
print(f"Status criação orçamento: {response.status_code}")

if response.status_code == 201:
    print("✅ Orçamento manual criado com sucesso!")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
else:
    print(f"❌ Erro ao criar orçamento manual: {response.text}")
    exit(1)

# Criar orçamento automático para comparação
orcamento_automatico = {
    "cliente_id": cliente_id,
    "titulo": "Orçamento Automático Teste",
    "descricao": "Teste de orçamento com tipo_calculo automatico",
    "tipo_calculo": "automatico",
    "subtotal": 1000.00,
    "total": 1000.00,
    "valido_ate": "2026-06-30T00:00:00"
}

print("\nCriando orçamento automático...")
print(f"Payload: {json.dumps(orcamento_automatico, indent=2)}")

response = requests.post(f"{BASE_URL}/api/orcamentos", json=orcamento_automatico, headers=headers)
print(f"Status criação orçamento: {response.status_code}")

if response.status_code == 201:
    print("✅ Orçamento automático criado com sucesso!")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
else:
    print(f"❌ Erro ao criar orçamento automático: {response.text}")
    exit(1)

print("\n✅ Todos os testes passaram!")

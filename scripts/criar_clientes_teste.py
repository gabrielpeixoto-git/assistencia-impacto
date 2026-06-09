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

# Clientes de teste
clientes_teste = [
    {
        'nome': 'João Silva',
        'email': 'joao.silva@email.com',
        'telefone': '11987654321',
        'whatsapp': '11987654321',
        'tipo_documento': 'cpf',
        'numero_documento': '12345678901',
        'tipo_cliente': 'residencial',
        'logradouro': 'Rua das Flores',
        'numero': '123',
        'complemento': 'Apto 4B',
        'bairro': 'Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01234567',
        'observacoes': 'Cliente VIP, prefere atendimento pela manhã'
    },
    {
        'nome': 'Empresa Tech Solutions Ltda',
        'email': 'contato@techsolutions.com.br',
        'telefone': '1134567890',
        'whatsapp': '11999998888',
        'tipo_documento': 'cnpj',
        'numero_documento': '12345678000190',
        'tipo_cliente': 'comercial',
        'logradouro': 'Av. Paulista',
        'numero': '1000',
        'complemento': 'Sala 15',
        'bairro': 'Bela Vista',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01310100',
        'observacoes': 'Contrato mensal de manutenção'
    },
    {
        'nome': 'Maria Santos',
        'email': 'maria.santos@email.com',
        'telefone': '21987654321',
        'whatsapp': '21987654321',
        'tipo_documento': 'cpf',
        'numero_documento': '98765432100',
        'tipo_cliente': 'residencial',
        'logradouro': 'Rua do Carmo',
        'numero': '456',
        'complemento': None,
        'bairro': 'Copacabana',
        'cidade': 'Rio de Janeiro',
        'estado': 'RJ',
        'cep': '22041002',
        'observacoes': None
    }
]

# Criar clientes
print("\n=== Criando clientes de teste ===")
for i, cliente in enumerate(clientes_teste, 1):
    req = urllib.request.Request(
        'http://localhost:8000/api/clientes',
        data=json.dumps(cliente).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        cliente_criado = json.loads(response.read().decode())
        print(f"\nCliente {i} criado com sucesso:")
        print(f"  ID: {cliente_criado['id']}")
        print(f"  Nome: {cliente_criado['nome']}")
        print(f"  Email: {cliente_criado['email']}")
        print(f"  Telefone: {cliente_criado['telefone']}")
        print(f"  Tipo: {cliente_criado['tipo_documento']} - {cliente_criado['tipo_cliente']}")

print("\n=== 3 clientes de teste criados com sucesso ===")

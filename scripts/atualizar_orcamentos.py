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

# Buscar orçamentos
print("Buscando orçamentos...")
req = urllib.request.Request('http://localhost:8000/api/orcamentos', headers=headers)
with urllib.request.urlopen(req) as response:
    orcamentos = json.loads(response.read().decode())
    print(f"Total de orçamentos: {len(orcamentos)}")

# Atualizar orçamentos para status ENVIADO
print("\nAtualizando orçamentos para status ENVIADO...")
for orc in orcamentos:
    update_data = {'status': 'enviado'}
    
    req = urllib.request.Request(
        f'http://localhost:8000/api/orcamentos/{orc["id"]}',
        data=json.dumps(update_data).encode('utf-8'),
        headers=headers,
        method='PUT'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  ✓ {orc['titulo']} atualizado para ENVIADO")

print("\n✓ Orçamentos atualizados com sucesso")

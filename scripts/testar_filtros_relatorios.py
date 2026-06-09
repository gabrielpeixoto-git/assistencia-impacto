"""
Script para testar os filtros de período nos endpoints de relatórios.
"""
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

periodos = ['hoje', 'semana', 'mes', 'trimestre']

for periodo in periodos:
    print(f"\n=== Testando período: {periodo} ===")
    
    # Testar endpoint /api/dashboard/resumo
    req = urllib.request.Request(
        f'http://localhost:8000/api/dashboard/resumo?periodo={periodo}',
        headers=headers,
        method='GET'
    )
    with urllib.request.urlopen(req) as response:
        dashboard_data = json.loads(response.read().decode())
        os_por_status = dashboard_data.get('os_por_status', [])
        total_os = sum(item['quantidade'] for item in os_por_status)
        print(f"  Dashboard - Total OS: {total_os}")
        print(f"  Dashboard - Receita: R$ {dashboard_data.get('receita_mes', 0):.2f}")
    
    # Testar endpoint /api/orcamentos/resumo
    req = urllib.request.Request(
        f'http://localhost:8000/api/orcamentos/resumo?periodo={periodo}',
        headers=headers,
        method='GET'
    )
    with urllib.request.urlopen(req) as response:
        orcamentos_data = json.loads(response.read().decode())
        print(f"  Orçamentos - Total: {orcamentos_data.get('total', 0)}")
        print(f"  Orçamentos - Aprovados: {orcamentos_data.get('aprovados', 0)}")
    
    # Testar endpoint /api/financeiro/dashboard
    req = urllib.request.Request(
        f'http://localhost:8000/api/financeiro/dashboard?periodo={periodo}',
        headers=headers,
        method='GET'
    )
    with urllib.request.urlopen(req) as response:
        financeiro_data = json.loads(response.read().decode())
        realizado = financeiro_data.get('realizado', {})
        print(f"  Financeiro - Receitas: R$ {realizado.get('receitas', 0):.2f}")
        print(f"  Financeiro - Despesas: R$ {realizado.get('despesas', 0):.2f}")
        print(f"  Financeiro - Saldo: R$ {realizado.get('saldo', 0):.2f}")

print("\n=== Testes concluídos ===")

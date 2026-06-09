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
    print("✓ Login realizado com sucesso")

headers = {'Authorization': f'Bearer {token}'}

# Testar GET /api/dashboard/resumo
print("\n=== Testando GET /api/dashboard/resumo ===")
req = urllib.request.Request('http://localhost:8000/api/dashboard/resumo', headers=headers)
with urllib.request.urlopen(req) as response:
    dashboard = json.loads(response.read().decode())
    print(f"Status: {response.status}")
    print("\nResumo do Dashboard:")
    print(f"  OS Hoje: {dashboard.get('os_hoje', 0)}")
    print(f"  OS Semana: {dashboard.get('os_semana', 0)}")
    print(f"  Receita Mensal: R$ {dashboard.get('receita_mes', 0):.2f}")
    print(f"  Lucro Mensal: R$ {dashboard.get('lucro_mes', 0):.2f}")
    print(f"  Orçamentos Pendentes: {dashboard.get('orcamentos_pendentes', 0)}")
    print(f"  Pagamentos Atrasados: {dashboard.get('pagamentos_atrasados', 0)}")
    print(f"  Estoque Crítico: {dashboard.get('itens_estoque_critico', 0)}")
    print(f"  OS Recentes: {len(dashboard.get('os_recentes', []))}")
    print(f"  Agenda Próximos Dias: {len(dashboard.get('agenda_proximos_dias', []))}")
    print(f"  Top Clientes: {len(dashboard.get('top_clientes', []))}")
    print(f"\n  Gráfico Receita: {dashboard.get('grafico_receita', [])}")

import requests
import json

# Testar endpoint de orçamentos
url = "http://localhost:8000/api/orcamentos"

# Primeiro fazer login para obter token
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "email": "admin@assistenciaimpacto.com.br",
    "senha": "admin123"
}

try:
    response = requests.post(login_url, json=login_data)
    print(f"Login status: {response.status_code}")
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Token obtido: {token[:20]}...")
        
        # Agora testar orçamentos
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        print(f"\nOrçamentos status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Número de orçamentos: {len(data)}")
            
            # Verificar se algum tem status null
            sem_status = [o for o in data if not o.get('status')]
            print(f"Orçamentos sem status: {len(sem_status)}")
            
            # Verificar se há registros null ou undefined
            registros_null = [o for o in data if o is None]
            print(f"Registros null: {len(registros_null)}")
            
            # Verificar se há registros com estrutura incompleta
            registros_incompletos = []
            for i, o in enumerate(data):
                if o is None:
                    continue
                campos_esperados = ['id', 'numero_orcamento', 'titulo', 'descricao', 'status', 'cliente_id']
                campos_faltando = [c for c in campos_esperados if c not in o]
                if campos_faltando:
                    registros_incompletos.append({'index': i, 'faltando': campos_faltando, 'dados': o})
            print(f"Registros com estrutura incompleta: {len(registros_incompletos)}")
            
            if data:
                print(f"\nPrimeiro orçamento:")
                print(json.dumps(data[0], indent=2, default=str))
                
                if sem_status:
                    print(f"\nOrçamento sem status:")
                    print(json.dumps(sem_status[0], indent=2, default=str))
                
                if registros_incompletos:
                    print(f"\nRegistro incompleto:")
                    print(json.dumps(registros_incompletos[0], indent=2, default=str))
        else:
            print(f"Erro: {response.text}")
    else:
        print(f"Erro no login: {response.text}")
except Exception as e:
    print(f"Erro: {e}")

import requests

print("=== Testando backend direto ===")
try:
    r = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"email": "admin@assistenciaimpacto.com.br", "senha": "admin123"}
    )
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:500]}")
except Exception as e:
    print(f"ERRO: {e}")

@echo off
cd /d "c:\Projeto Impacto Soluções\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

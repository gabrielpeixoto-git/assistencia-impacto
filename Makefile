.PHONY: test-backend test-e2e test-all test-clean e2e-report coverage

test-backend:
@echo Rodando testes de integracao backend...
docker compose -f docker-compose.test.yml run --rm backend_e2e sh -c "pytest tests/integration/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html:/reports/coverage --asyncio-mode=auto -n auto"

e2e-build:
@echo Construindo imagens para E2E...
docker compose -f docker-compose.test.yml build --no-cache

e2e-up:
@echo Subindo stack E2E...
docker compose -f docker-compose.test.yml up -d banco_e2e redis_e2e backend_e2e nginx_e2e
@echo Aguardando stack ficar pronta...
@until curl -sf http://localhost:9090/health; do echo Aguardando...; sleep 3; done
@echo Stack E2E pronta em http://localhost:9090

e2e-run:
@echo Rodando testes Playwright...
cd e2e && npx playwright test --reporter=list

test-e2e: e2e-build e2e-up
@echo Rodando testes Playwright via Docker...
docker compose -f docker-compose.test.yml run --rm playwright_e2e
make test-clean-e2e

test-all: test-backend test-e2e
@echo Suite completa finalizada!

test-clean-e2e:
docker compose -f docker-compose.test.yml down --remove-orphans

test-clean:
docker compose -f docker-compose.test.yml down -v --remove-orphans
rm -rf reports/ e2e/.auth/

e2e-report:
cd e2e && npx playwright show-report ../reports/playwright-html

coverage:
@echo Abra: reports/coverage/index.html

debug-backend:
docker compose -f docker-compose.test.yml exec backend_e2e bash

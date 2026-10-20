.PHONY: install test phase1-up migrate seed run-api run-worker

install:
	python3 -m pip install -U pip
	python3 -m pip install -r requirements-dev.txt

test:
	PYTHONPATH=apps/api python3 -m pytest apps/api/tests -q

phase1-up:
	./scripts/bootstrap/phase1-up.sh

migrate:
	PYTHONPATH=. alembic upgrade head

seed:
	PYTHONPATH=.:apps/api python3 scripts/seed.py

run-api:
	PYTHONPATH=apps/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	PYTHONPATH=apps/worker uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

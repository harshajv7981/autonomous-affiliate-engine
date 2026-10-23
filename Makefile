.PHONY: install test phase1-up migrate seed send-test send-test-live add-offer import-commissions run-api run-worker

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

send-test:
	PYTHONPATH=.:apps/api python3 scripts/send_test.py

send-test-live:
	PYTHONPATH=.:apps/api python3 scripts/send_test.py --send

add-offer:
	PYTHONPATH=.:apps/api python3 scripts/add_offer.py $(ARGS)

import-commissions:
	PYTHONPATH=.:apps/api python3 scripts/import_commissions.py $(ARGS)

run-api:
	PYTHONPATH=apps/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	PYTHONPATH=apps/worker uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

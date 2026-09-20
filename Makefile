.PHONY: install test run-api run-worker

install:
	python3 -m pip install -U pip
	python3 -m pip install -r <(python3 -c "print('fastapi[standard]>=0.128.0\npydantic-settings>=2.11.0\nhttpx>=0.28.0\npytest>=8.4.0')")

test:
	PYTHONPATH=apps/api python3 -m pytest apps/api/tests -q

run-api:
	PYTHONPATH=apps/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	PYTHONPATH=apps/worker uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

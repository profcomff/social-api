run:
	source ./venv/bin/activate && uvicorn --reload --log-config logging_dev.conf social.routes.base:app

format: configure
	source ./venv/bin/activate && autoflake -r --in-place --remove-all-unused-imports ./social
	source ./venv/bin/activate && isort ./social
	source ./venv/bin/activate && black ./social

configure: venv
	source ./venv/bin/activate && pip install -r requirements.dev.txt -r requirements.txt

venv:
	python3.11 -m venv venv

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-social postgres:15

migrate:
	source ./venv/bin/activate && alembic upgrade head

test:
	source ./venv/bin/activate && python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG

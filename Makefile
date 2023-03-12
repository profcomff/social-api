run:
	source ./venv/bin/activate && uvicorn --reload --log-config logging_test.conf social.routes.base:app

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-social postgres:15
	sleep 3

migrate:
	alembic upgrade head

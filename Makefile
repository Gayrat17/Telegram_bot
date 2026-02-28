alembic_init:
	alembic init migrations

up:
	alembic upgrade head

down:
	alembic downgrade -1

mig:
	alembic revision --autogenerate -m "massage"
.PHONY: make-migs
make-migs:
	python3 manage.py makemigrations

.PHONY: migrate
migrate:
	python3 manage.py migrate

.PHONY: mm
mm: make-m migrate

.PHONY: admin
admin:
	python3 manage.py createsuperuser

.PHONY: run
run:
	python3 manage.py runserver 0.0.0.0:8000

.PHONY: deps
deps:
	pip install -r requirements/python/base.txt

.PHONY: test-deps
test-deps:
	pip install -r requirements/python/test.txt

.PHONY: dev-deps
dev-deps:
	pip install -r requirements/python/dev.txt

.PHONY: pre-commit-install
pre-commit-install: dev-deps
	pre-commit install

.PHONY: migrate
migrate:
	python3 manage.py migrate

.PHONY: run
run:
	python3 manage.py runserver 0.0.0.0:8000

.PHONY: lint
lint: test-deps
	flake8 .
	black --check .
	isort --check-only .
	mypy .
	pre-commit run -a

.PHONY: lint-fix
lint-fix: test-deps
	black .
	isort .
	pre-commit run

.PHONY: test
test: test-deps
	pytest --disable-pytest-warnings --verbose --reuse-db --nomigrations

.PHONY: up
up:
	./manage.py runserver

.PHONY: init-ansible
init-ansible:
	ansible-galaxy collection install community.docker --force
	ansible-galaxy install geerlingguy.docker

.PHONY: ansible-instance
ansible-instance:
	ansible-playbook -i ansible/inventory.ini ansible/setup_instance.yaml

.PHONY: ansible-nginx
ansible-nginx:
	ansible-playbook -i ansible/inventory.ini ansible/deploy/nginx.yaml

.PHONY: ansible-app
ansible-app:
	set -o allexport; source production.env; set +o allexport; \
	ansible-playbook -i ansible/inventory.ini ansible/deploy/app.yaml

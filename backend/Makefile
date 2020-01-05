.PHONY: format
format:
	pipenv run isort --apply
	pipenv run black .

.PHONY: check
check:
	pipenv run flake8

.PHONY: release
release:
	docker build . -t zeebonk/wedding:backend
	docker push zeebonk/wedding:backend

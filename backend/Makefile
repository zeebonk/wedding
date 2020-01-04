.PHONY: format
format:
	pipenv run isort --apply
	pipenv run black .

.PHONY: check
check:
	pipenv run flake8

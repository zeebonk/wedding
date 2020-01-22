.PHONY: format
format:
	pipenv run isort --apply
	pipenv run black .

.PHONY: check
check:
	pipenv run pylint wedding \
	    -d missing-class-docstring \
	    -d missing-function-docstring \
	    -d missing-module-docstring \
	    -d bad-continuation \
	    -d invalid-name \
	    -d too-many-arguments

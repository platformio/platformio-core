
lint:
	pylint --rcfile=./.pylintrc ./platformio

isort:
	isort -rc ./platformio
	isort -rc ./tests
	isort -rc ./scripts

yapf:
	yapf --recursive --in-place platformio/

before-commit: isort yapf pylint

clean-docs:
	rm -rf docs/_build

clean: clean-docs
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf .cache
	rm -rf build
	rm -rf htmlcov
	rm -f .coverage
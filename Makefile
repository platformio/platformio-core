
lint:
	pylint --rcfile=./.pylintrc ./platformio

isort:
	isort -rc ./platformio

clean-docs:
	rm -rf docs/_build

clean: clean-docs
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf .cache
	rm -rf build
	rm -rf htmlcov
	rm -f .coverage
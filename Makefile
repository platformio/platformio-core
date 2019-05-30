
lint:
	pylint --rcfile=./.pylintrc ./platformio

isort:
	isort -rc ./platformio
	isort -rc ./tests

yapf:
	yapf --recursive --in-place platformio/

test:
	py.test --verbose --capture=no --exitfirst -n 3 --dist=loadscope tests --ignore tests/test_examples.py --ignore tests/test_pkgmanifest.py

before-commit: isort yapf lint test

clean-docs:
	rm -rf docs/_build

clean: clean-docs
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf .cache
	rm -rf build
	rm -rf htmlcov
	rm -f .coverage
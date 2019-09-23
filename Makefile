lint:
	pylint --rcfile=./.pylintrc ./platformio

isort:
	isort -rc ./platformio
	isort -rc ./tests

black:
	black --target-version py27 ./platformio
	black --target-version py27 ./tests

test:
	py.test --verbose --capture=no --exitfirst -n 3 --dist=loadscope tests --ignore tests/test_examples.py --ignore tests/test_pkgmanifest.py

before-commit: isort black lint test

clean-docs:
	rm -rf docs/_build

clean: clean-docs
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf .cache
	rm -rf build
	rm -rf htmlcov
	rm -f .coverage

profile:
	# Usage $ > make PIOARGS="boards" profile
	python -m cProfile -o .tox/.tmp/cprofile.prof $(shell which platformio) ${PIOARGS}
	snakeviz .tox/.tmp/cprofile.prof

publish:
	python setup.py sdist upload

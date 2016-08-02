
lint:
	pylint --rcfile=./.pylintrc ./platformio

isort:
	isort -rc ./platformio

clean:
	find . -name \*.pyc -delete
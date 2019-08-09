NAME=waitress

lint:
	black . && isort -rc .

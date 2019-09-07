NAME=folly

lint:
	black . && isort -rc .

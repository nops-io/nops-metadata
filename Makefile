test:
	pytest -n auto nops_metadata/

publish: test build
	poetry publish

build:
	poetry build

test:
	pytest -n auto nops_metadata/

publish: test build
	poetry publish

build:
	poetry build

setup:
	python3 setup.py sdist bdist_wheel

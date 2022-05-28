test:
	pytest nops_metadata/

publish: build
	poetry publish

build:
	poetry build

setup:
	python3 setup.py sdist bdist_wheel

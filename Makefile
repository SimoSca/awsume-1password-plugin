.PHONY: build clean publish

build:
	python3 setup.py bdist_wheel

clean:
	rm -Rf build dist *.egg-info

publish:
	# with __token__ you have to insert you API TOKEN setted into PYPI
	twine upload --username __token__ dist/*

init:
	pip install -r requirements.txt --use-mirrors

test:
	cd tests;nosetests 
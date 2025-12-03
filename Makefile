.PHONY: setup run install clean

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	mkdir -p uploads downloads
	@echo "Setup complete! Don't forget to create a .env file with your OPENAI_API_KEY"

install:
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python src/app.py

clean:
	rm -rf uploads/* downloads/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

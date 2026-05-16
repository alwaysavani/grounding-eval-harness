.PHONY: setup test clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

test: setup
	.venv/bin/python src/app.py --resume data/base_resume.md --job data/job_postings/job_1.txt

clean:
	rm -rf .venv
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

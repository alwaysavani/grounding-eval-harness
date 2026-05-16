.PHONY: setup test clean api ui

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	cd ui && npm install

test: setup
	.venv/bin/python src/app.py --resume data/base_resume.md --job data/job_postings/job_1.txt

api:
	.venv/bin/uvicorn src.api:app --reload

ui:
	cd ui && npm run dev

clean:
	rm -rf .venv ui/node_modules ui/.next
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

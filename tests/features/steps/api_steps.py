from behave import given, when, then
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))
import api as api_module
from api import app

client = TestClient(app)

MOCK_STATE = {
    "draft_resume": "<resume># My Tailored Resume\n\n## Experience\n- Python Developer at TechCorp</resume>\nNote: removed unsupported claims.",
    "iteration_count": 1,
    "hallucinations_found": False,
    "evaluation_feedback": ""
}

@given('the FastAPI application is running')
def step_impl(context):
    context.client = client

@when('I send a POST request to "{endpoint}" with a valid base resume and job description')
def step_impl(context, endpoint):
    # Patch the run_pipeline wrapper — avoids touching the immutable CompiledStateGraph
    with patch("api.run_pipeline", return_value=MOCK_STATE):
        response = context.client.post(endpoint, json={
            "base_resume_text": "Jane Doe. Backend Developer at TechCorp 2020-present. Skills: Python, FastAPI.",
            "job_description_text": "We are looking for a Python Backend Engineer with FastAPI experience.",
            "output_format": "Markdown"
        })
        context.response = response

@then('the response status code should be {status_code:d}')
def step_impl(context, status_code):
    assert context.response.status_code == status_code, \
        f"Expected {status_code}, got {context.response.status_code}. Body: {context.response.text}"

@then('the response should contain "{key}"')
def step_impl(context, key):
    json_data = context.response.json()
    assert key in json_data, f"Key '{key}' not found in response. Response: {json_data}"

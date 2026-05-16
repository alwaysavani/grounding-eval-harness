from behave import given, when, then
import sys
import os
from langgraph.graph import END

# Add src to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))
from app import route_next

@given('the iteration count is {count:d}')
def step_impl(context, count):
    if not hasattr(context, 'state'):
        context.state = {}
    context.state["iteration_count"] = count

@given('hallucinations were found')
def step_impl(context):
    if not hasattr(context, 'state'):
        context.state = {}
    context.state["hallucinations_found"] = True

@given('no hallucinations were found')
def step_impl(context):
    if not hasattr(context, 'state'):
        context.state = {}
    context.state["hallucinations_found"] = False

@when('the router evaluates the state')
def step_impl(context):
    context.result = route_next(context.state)

@then('the next node should be "{node}"')
def step_impl(context, node):
    expected = END if node == "__end__" else node
    assert context.result == expected, f"Expected {expected}, got {context.result}"

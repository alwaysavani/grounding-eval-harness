import os
import sys

# Add src/ to sys.path so that internal imports like 'from schemas import...' work
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from schemas import AgentState
from tailor_agent import generate_draft
from grounding_harness import evaluate_draft

load_dotenv()

app = FastAPI(title="Anti-Hallucination Resume Grounding API")

# Setup CORS for the NextJS UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Restricted to local UI origins
    allow_credentials=True,
    allow_methods=["POST"], # Restrict to POST
    allow_headers=["*"],
)

class ResumeRequest(BaseModel):
    base_resume_text: str = Field(..., max_length=20000, description="Base resume content, capped to prevent payload DoS")
    job_description_text: str = Field(..., max_length=20000, description="Job posting content, capped to prevent payload DoS")
    output_format: str = "Markdown"

def route_next(state: AgentState):
    if state.get("hallucinations_found") and state.get("iteration_count", 0) < 3:
        return "generator"
    return END

# Build Graph once
workflow = StateGraph(AgentState)
workflow.add_node("generator", generate_draft)
workflow.add_node("evaluator", evaluate_draft)
workflow.set_entry_point("generator")
workflow.add_edge("generator", "evaluator")
workflow.add_conditional_edges(
    "evaluator",
    route_next,
    {
        "generator": "generator",
        END: END
    }
)
langgraph_app = workflow.compile()

import re

@app.post("/api/tailor")
async def tailor_resume(request: ResumeRequest):
    if not request.base_resume_text or not request.job_description_text:
        raise HTTPException(status_code=400, detail="base_resume_text and job_description_text are required")
        
    initial_state = {
        "base_resume_text": request.base_resume_text,
        "job_description_text": request.job_description_text,
        "draft_resume": "",
        "evaluation_feedback": "",
        "hallucinations_found": False,
        "iteration_count": 0,
        "output_format": request.output_format
    }
    
    try:
        final_state = langgraph_app.invoke(initial_state)
        draft = final_state.get("draft_resume", "")
        
        resume_match = re.search(r"<resume>(.*?)</resume>", draft, re.DOTALL)
        if resume_match:
            parsed_resume = resume_match.group(1).strip()
            agent_notes = re.sub(r"<resume>.*?</resume>", "", draft, flags=re.DOTALL).strip()
        else:
            parsed_resume = draft.strip()
            agent_notes = ""

        return {
            "status": "success",
            "draft_resume": parsed_resume,
            "agent_notes": agent_notes,
            "iteration_count": final_state.get("iteration_count"),
            "hallucinations_found": final_state.get("hallucinations_found"),
            "evaluation_feedback": final_state.get("evaluation_feedback")
        }
    except Exception as e:
        # Return generic error to prevent internal API/LLM error leakage
        raise HTTPException(status_code=500, detail="An internal pipeline error occurred. Please try again later.")

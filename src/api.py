import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    allow_origins=["*"], # In production, restrict to your UI domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeRequest(BaseModel):
    base_resume_text: str
    job_description_text: str
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
        return {
            "status": "success",
            "draft_resume": final_state.get("draft_resume"),
            "iteration_count": final_state.get("iteration_count"),
            "hallucinations_found": final_state.get("hallucinations_found"),
            "evaluation_feedback": final_state.get("evaluation_feedback")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

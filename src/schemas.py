from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field

# LangGraph State
class AgentState(TypedDict):
    base_resume_text: str
    job_description_text: str
    draft_resume: str
    evaluation_feedback: str
    hallucinations_found: bool
    iteration_count: int

# Pydantic model for structured output from the Evaluator
class Claim(BaseModel):
    claim_text: str = Field(description="The exact measurable claim extracted from the draft resume.")
    is_supported: bool = Field(description="True if the claim is explicitly backed by the base resume, False otherwise.")
    explanation: str = Field(description="Explanation of why the claim is or is not supported by the base resume.")

class EvaluatorOutput(BaseModel):
    claims: List[Claim] = Field(description="List of extracted claims and their evaluation.")
    hallucinations_found: bool = Field(description="True if any claim is NOT supported by the base resume.")
    evaluation_feedback: str = Field(description="Detailed feedback describing which claims are hallucinations. Empty if none found.")

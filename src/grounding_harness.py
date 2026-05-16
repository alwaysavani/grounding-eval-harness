import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from schemas import AgentState, EvaluatorOutput
from rich.console import Console

console = Console()

def evaluate_draft(state: AgentState) -> dict:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    structured_llm = llm.with_structured_output(EvaluatorOutput)
    
    system_prompt = (
        "You are a strict evaluation harness. Your job is to extract measurable claims "
        "(years of experience, skills, metrics, achievements) from a draft resume and verify if they are explicitly backed by the base resume. "
        "Be extremely strict. If a claim in the draft is not clearly supported by the base resume, it is a hallucination. "
        "Output the results in the required JSON format."
    )
    
    human_prompt = (
        "Base Resume (Source of Truth):\n{base_resume}\n\n"
        "Draft Resume to Evaluate:\n{draft_resume}\n\n"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({
        "base_resume": state.get("base_resume_text", ""),
        "draft_resume": state.get("draft_resume", "")
    })
    
    if isinstance(result, dict):
        hallucinations_found = result.get("hallucinations_found", False)
        evaluation_feedback = result.get("evaluation_feedback", "")
    else:
        hallucinations_found = getattr(result, "hallucinations_found", False)
        evaluation_feedback = getattr(result, "evaluation_feedback", "")
        
    if hallucinations_found:
        console.print("[bold red]❌ Hallucinations Detected![/bold red]")
        console.print(f"[red]Feedback: {evaluation_feedback}[/red]")
    else:
        console.print("[bold green]✅ All claims verified successfully. No hallucinations found.[/bold green]")
        
    return {
        "hallucinations_found": hallucinations_found,
        "evaluation_feedback": evaluation_feedback
    }

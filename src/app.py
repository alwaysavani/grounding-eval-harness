import argparse
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from schemas import AgentState
from tailor_agent import generate_draft
from grounding_harness import evaluate_draft
from rich.console import Console

console = Console(stderr=True)

def route_next(state: AgentState):
    if state.get("hallucinations_found") and state.get("iteration_count", 0) < 3:
        console.print("[yellow]Looping back to Generator to correct hallucinations...[/yellow]")
        return "generator"
    return END

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Anti-Hallucination Resume Grounding Harness")
    parser.add_argument("--resume", required=True, help="Path to the base resume markdown file")
    parser.add_argument("--job", required=True, help="Path to the job description text file")
    args = parser.parse_args()
    
    if not os.path.exists(args.resume):
        console.print(f"[bold red]Error: Base resume file not found at {args.resume}[/bold red]")
        return
        
    if not os.path.exists(args.job):
        console.print(f"[bold red]Error: Job description file not found at {args.job}[/bold red]")
        return
        
    with open(args.resume, "r", encoding="utf-8") as f:
        base_resume_text = f.read()
        
    with open(args.job, "r", encoding="utf-8") as f:
        job_description_text = f.read()
        
    # Build LangGraph
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
    
    app = workflow.compile()
    
    _, ext = os.path.splitext(args.resume)
    output_format = "LaTeX" if ext.lower() == ".tex" else "Markdown"
    
    initial_state = {
        "base_resume_text": base_resume_text,
        "job_description_text": job_description_text,
        "draft_resume": "",
        "evaluation_feedback": "",
        "hallucinations_found": False,
        "iteration_count": 0,
        "output_format": output_format
    }
    
    console.print("[bold blue]Starting Anti-Hallucination Resume Pipeline...[/bold blue]")
    
    final_state = app.invoke(initial_state)
    draft = final_state.get("draft_resume", "")
    
    import re
    resume_match = re.search(r"<resume>(.*?)</resume>", draft, re.DOTALL)
    if resume_match:
        parsed_resume = resume_match.group(1).strip()
    else:
        parsed_resume = draft.strip()
    
    # Print ONLY the tailored resume to stdout
    print(parsed_resume)

if __name__ == "__main__":
    main()

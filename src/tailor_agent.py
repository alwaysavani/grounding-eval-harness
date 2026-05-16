import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from schemas import AgentState

def generate_draft(state: AgentState) -> dict:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    
    system_prompt = (
        "You are an expert resume writer. Your task is to tailor a base resume to a specific job description. "
        "You MUST only use the facts, skills, and metrics provided in the base resume. DO NOT invent or hallucinate any information. "
        "If evaluation feedback is provided, you must use it to correct any previous hallucinations by removing unsupported claims."
    )
    
    human_prompt = (
        "Base Resume:\n{base_resume}\n\n"
        "Job Description:\n{job_description}\n\n"
    )
    
    if state.get("evaluation_feedback") and state.get("hallucinations_found"):
        human_prompt += "Previous Evaluation Feedback (Correct these hallucinations):\n{feedback}\n\n"
        
    output_format = state.get("output_format", "Markdown")
    human_prompt += f"Draft the tailored resume now in {output_format} format. Do not include markdown code blocks around the text, just output the raw code."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "base_resume": state.get("base_resume_text", ""),
        "job_description": state.get("job_description_text", ""),
        "feedback": state.get("evaluation_feedback", "")
    })
    
    return {
        "draft_resume": response.content,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

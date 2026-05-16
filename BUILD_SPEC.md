# 🚀 Antigravity Implementation Spec: Anti-Hallucination Resume Grounding Harness

## 🎯 Primary Objective
Build a Python-based agentic pipeline that tailors a resume to a specific job description, wrapped in a strict evaluation harness. The system must catch and reject LLM hallucinations by verifying that every claim in the generated resume is deterministically backed by the source-of-truth base resume.

## 🛠️ Tech Stack & Constraints
*   **Language:** Python 3.10+
*   **Orchestration:** LangGraph (State machine loop)
*   **LLM Inference:** Groq Python SDK (`llama3-8b-8192` or `llama3-70b-8192`)
*   **Data Validation:** Pydantic (Strict structured outputs)
*   **Terminal Output:** Rich (For green/red evaluation logs)
*   **Constraint:** Do NOT use OpenAI, Anthropic, or any paid APIs. Strictly rely on Groq.

## 📁 Required Directory Structure
Create the following structure:
├── .env.example
├── Makefile
├── requirements.txt
├── src/
│   ├── app.py              # Main LangGraph execution script
│   ├── api.py              # FastAPI presentation layer
│   ├── tailor_agent.py     # Generator node logic
│   ├── grounding_harness.py# Evaluation node logic
│   └── schemas.py          # Pydantic models
├── ui/                     # Next.js Presentation Layer
└── data/
    ├── base_resume.md      # Dummy base resume for testing
    └── job_postings/
        └── job_1.txt       # Dummy job description for testing

## 🧠 Core System Architecture

### 1. State Definition (`schemas.py`)
Define a LangGraph state dictionary/Pydantic model that holds:
*   `base_resume_text` (str)
*   `job_description_text` (str)
*   `draft_resume` (str)
*   `evaluation_feedback` (str)
*   `hallucinations_found` (bool)
*   `iteration_count` (int)

### 2. The Generator Node (`tailor_agent.py`)
*   **Input:** `base_resume_text`, `job_description_text`, and optionally `evaluation_feedback`.
*   **Logic:** Uses Groq to draft a resume tailored to the job. If `evaluation_feedback` exists, it must use that feedback to correct previous hallucinations.
*   **Output:** Updates `draft_resume`.

### 3. The Evaluator Node (`grounding_harness.py`)
*   **Input:** `draft_resume`, `base_resume_text`.
*   **Logic:** Uses Groq to extract all measurable claims (years of experience, skills, metrics) from the draft. It then strictly checks if each claim exists in the `base_resume_text`.
*   **Output:** If a claim is unsupported, set `hallucinations_found = True` and populate `evaluation_feedback` with exact details of the lie. If all claims are supported, set `hallucinations_found = False`. Use the `Rich` library to print a red warning for failures and a green success message for passes.

### 4. The Graph Orchestrator (`app.py`)
*   Build the LangGraph flow:
    1. Start -> `Generator Node`
    2. `Generator Node` -> `Evaluator Node`
    3. `Evaluator Node` -> Conditional Edge:
        *   If `hallucinations_found == True` AND `iteration_count < 3` -> loop back to `Generator Node`.
        *   If `hallucinations_found == False` OR `iteration_count >= 3` -> End.

## 🤖 Antigravity Agent Execution Steps
Please execute the following steps sequentially. Do not proceed to the next step until the previous one is fully implemented and free of syntax errors.

1.  **Scaffold:** Create the directory structure, `.env.example`, and `requirements.txt` containing `groq`, `langgraph`, `pydantic`, `python-dotenv`, and `rich`.
2.  **Define Types:** Implement `src/schemas.py` using Pydantic.
3.  **Implement LLM Logic:** Write the Groq API calls with standard system prompts in `src/tailor_agent.py` and `src/grounding_harness.py`. Ensure Pydantic is used for structured JSON extraction in the evaluator.
4.  **Wire Graph:** Build the LangGraph state machine in `src/app.py`. Add basic CLI argument parsing (`argparse`) to accept file paths for the resume and job description.
5.  **Mock Data:** Generate a simple Markdown resume in `data/base_resume.md` and a dummy tech job description in `data/job_postings/job_1.txt` so the system can be tested immediately.
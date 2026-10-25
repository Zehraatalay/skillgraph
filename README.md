SkillGraph

Evidence-Backed Skill Analysis & Explainable Job Matching

SkillGraph is an AI-powered application that analyzes technical skills from CVs and GitHub repositories, then evaluates how well they align with job requirements.

It combines structured skill extraction, deterministic and semantic matching, and traceable evidence to provide explainable results rather than relying solely on keyword matching.

Features

* CV & GitHub Analysis: Extracts technical skills from CV text, PDF/DOCX documents, and GitHub source code.
* Evidence-Based Evaluation: Distinguishes between self-reported, implementation-backed, and tested skills.
* Job Requirement Extraction: Identifies required and preferred qualifications, including ALL and ANY requirement groups.
* Hybrid Skill Matching: Combines exact, alias, and hierarchical matching with LLM-based semantic evaluation.
* Explainable Results: Provides requirement coverage, full/partial/missing matches, and supporting CV or GitHub evidence.
* Multiple Job Comparison: Evaluates a candidate against multiple job descriptions.
* Caching & Fallback: Caches extraction results and preserves deterministic matches when semantic matching fails.

Tech Stack

Component	Technologies
Backend	Python 3.11, FastAPI, Pydantic
AI & Orchestration	LangGraph, LangChain, Google Gemini
Frontend	Vue 3, Vite
Deployment	Docker, Docker Compose, Nginx
Testing	pytest
Experimental	Ollama

Architecture

The application uses a LangGraph workflow to coordinate candidate analysis, job requirement extraction, and matching.

CV / GitHub
     |
     v
Candidate Skill & Evidence Extraction
     |
     v
Candidate Profile
     |
     +----------------------+
     |                      |
     v                      v
Candidate Evidence     Job Requirements
     |                      |
     +-----------+----------+
                 |
                 v
       Deterministic Matching
                 |
                 v
        Semantic Matching
        (Unmatched Skills)
                 |
                 v
      Explainable Job Results
                 |
                 v
            Vue Frontend

Semantic matching supplements deterministic matching. If the LLM provider is unavailable, deterministic results are retained.

Getting Started

Prerequisites

* Docker and Docker Compose
* Google Gemini API key
* GitHub personal access token (recommended)

1. Clone the Repository

git clone https://github.com/Zehraatalay/skillgraph.git
cd skillgraph

2. Configure Environment Variables

cp .env.example .env

Update .env with your credentials:

LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=your_supported_model
GITHUB_TOKEN=your_github_personal_access_token

Never commit actual API keys or tokens.

3. Run the Application

docker compose up --build -d

Open the application:

http://localhost:8080/skill-analysis

Verify backend health:

curl http://localhost:8080/api/health

Stop the application:

docker compose down

API Endpoints

Method	Endpoint	Description
GET	/health	Backend health check
POST	/analyze	Candidate analysis and job matching
POST	/documents/extract	PDF/DOCX text extraction

When accessing the backend through Nginx, prefix endpoints with /api/.

The application accepts CV-only, GitHub-only, or combined candidate inputs. At least one candidate source is required.

Document uploads are limited to 5 MB.

Testing & Evaluation

Run backend tests:

pytest agents/tests -q

Latest result: 257 tests passed.

The test suite covers skill extraction, evidence validation, workflow routing, deterministic and semantic matching, fallback behavior, and API integration.

Build the frontend:

cd frontend
npm ci
npm run build

Evaluation datasets and baseline results are included for experimenting with matching quality.

Limitations

* LLM-powered extraction and semantic matching depend on provider availability and API quotas.
* Deterministic fallback may miss semantically related skills that are not explicitly mapped.
* GitHub analysis examines selected repositories rather than a developer’s complete history.
* Evidence-backed matching is an approximation of demonstrated skills, not a definitive proficiency assessment.
* Ollama integration is experimental.

Project Status

Functional prototype

The core workflow, frontend, Docker deployment, and automated tests are implemented.

A real CV + GitHub analysis has been executed through Docker. During testing, Gemini quota exhaustion triggered the deterministic matching fallback successfully.

GitHub-only routing is covered by automated tests; separate live end-to-end validation is pending.

Author

Zehra Atalay
Computer Engineering Graduate

GitHub: Zehraatalay
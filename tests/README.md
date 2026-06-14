# Irish Immigration Navigator

An AI-powered Irish immigration assistant built with LangGraph, RAG, and Groq. Answers immigration questions, generates personalised checklists, and explains official documents — all grounded in live Irish government sources.

Built as a portfolio project demonstrating production-grade multi-agent AI engineering.

---

## What it does

**Ask any immigration question** and get an accurate, sourced answer in plain English:
> "Can I work while on a student visa in Ireland?"
> "What is the salary threshold for a Critical Skills Employment Permit?"
> "How long does naturalisation take?"

**Generate a personalised checklist** based on your nationality, current status, and goal:
> Goal: Apply for Critical Skills EP | Nationality: Indian | Status: Stamp 2
> → 5-step action plan with documents, fees, timelines, and official links

**Explain immigration letters and forms** in plain language:
> "I received a letter saying my Stamp 2 is expiring. What do I do?"
> → Clear explanation of what it means and exactly what action to take

Every answer includes the official source URL so users can verify independently.

---

## Architecture


User question

↓

Supervisor Agent  (Groq Llama3 — routes to right specialist)

↓

┌─────────────┬──────────────┬──────────────────┐

│  RAG Agent  │  Checklist   │  Document Agent  │

│             │    Agent     │                  │

│ Factual     │ Step-by-step │ Explains forms   │

│ questions   │ action plans │ and letters      │

└─────────────┴──────────────┴──────────────────┘

↓

FAISS vector search over 16 official Irish government pages

↓

Grounded answer with source citations

**Why LangGraph:** State is typed and managed. Adding a new agent is adding a new node. Conditional edges make routing explicit and testable. Built-in async support.

**Why RAG over fine-tuning:** Immigration rules change frequently. RAG retrieves from current documents on every query — a fine-tuned model would go stale.

**Why local embeddings:** `sentence-transformers/all-MiniLM-L6-v2` runs entirely locally. No API cost per query, no rate limits, no latency from external calls.

---

## Key engineering decisions

### Grounding over generation
Every answer is grounded in retrieved chunks from official sources. The LLM cannot hallucinate requirements because it only answers from what the retriever returns. If no relevant context is found, it says so and points to the official website.

### Structured outputs
Checklists are structured JSON — not free-form text. Each step has a title, description, documents required, estimated time, fee, and official link. A frontend can render this properly rather than parsing prose.

### Agent specialisation
Three specialist agents each do one thing well rather than one agent doing everything poorly. The supervisor routes based on intent — factual question, action plan, or document explanation.

### Disclaimer on every response
Every API response includes a disclaimer that the information is for guidance only and should be verified with official sources. This is the right thing to do and protects users who might act on outdated information.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Agent orchestration | LangGraph |
| LLM | Groq (Llama3 70B) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local) |
| Vector store | FAISS |
| Knowledge base | 16 official Irish government pages |
| API framework | FastAPI + Uvicorn |
| Database | PostgreSQL 16 + SQLAlchemy async |
| Validation | Pydantic v2 |
| Logging | structlog |
| Infra | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Running locally

### Prerequisites
- Docker Desktop
- Groq API key — free at [console.groq.com](https://console.groq.com)

### Setup

```bash
# 1. Clone
git clone https://github.com/priyanka603/immigration-navigator
cd immigration-navigator

# 2. Create .env
cp .env.template .env
# Add your GROQ_API_KEY and generate a SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Start the stack
docker compose up --build

# 4. Build the knowledge base (first time only)
docker compose exec app python scripts/ingest.py
```

### Verify

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"immigration-navigator","version":"0.1.0"}
```

Open Swagger UI: http://localhost:8000/docs

---

## API endpoints

### Ask a question
```bash
POST /api/v1/chat
{
  "message": "Can I work while on a student visa in Ireland?",
  "nationality": "Indian",
  "current_visa": "Stamp 2"
}
```

### Generate a checklist
```bash
POST /api/v1/chat/checklist
{
  "goal": "Apply for Critical Skills Employment Permit",
  "nationality": "Indian",
  "current_status": "Student Stamp 2"
}
```

### Get conversation history
```bash
GET /api/v1/chat/history/{session_id}
```

---

## Knowledge base

The system is grounded in 16 official Irish government pages across these sources:

| Source | Pages |
|--------|-------|
| citizensinformation.ie | Visas, employment permits, citizenship, residence |
| irishimmigration.ie | Work options, study, registration, permit changes |

Pages are saved locally and ingested into a FAISS vector index. The index contains 66 chunks across all pages. Run `python scripts/ingest.py` to rebuild after adding new sources.

---

## Project structure


immigration-navigator/

├── app/

│   ├── agents/

│   │   ├── supervisor.py      # Routes questions to right agent

│   │   ├── rag_agent.py       # Answers factual questions from docs

│   │   ├── checklist_agent.py # Generates step-by-step plans

│   │   └── document_agent.py  # Explains letters and forms

│   ├── graph/

│   │   ├── state.py           # LangGraph shared state

│   │   └── workflow.py        # Agent graph definition

│   ├── rag/

│   │   ├── sources.py         # Government URLs and filenames

│   │   ├── ingestion.py       # Build FAISS index from HTML files

│   │   └── retriever.py       # Search the FAISS index

│   ├── api/routes/            # FastAPI endpoints

│   ├── schemas/               # Pydantic request/response models

│   ├── db/                    # PostgreSQL models

│   └── core/                  # Config, logging

├── data/

│   ├── raw_html/              # Saved government pages

│   └── faiss_index/           # Vector index (gitignored)

├── scripts/

│   ├── ingest.py              # Build knowledge base

│   └── test_graph.py          # Test multi-agent workflow

└── tests/

---

## Disclaimer

This tool is for general guidance only. Information is sourced from publicly available Irish government websites. Immigration rules change frequently. Always verify requirements directly with the [Irish Immigration Service](https://www.irishimmigration.ie) or [Citizens Information](https://www.citizensinformation.ie) before making any immigration decisions.
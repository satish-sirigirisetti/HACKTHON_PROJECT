# CareerAI

CareerAI is a student-focused career intelligence platform foundation. It is structured to grow from durable student and career data into explainable recommendations, skill-gap analysis, personalized learning, and retrieval-grounded AI guidance.

## Problem

Students often have to connect academic experience, skills, projects, and learning options across disconnected sources. CareerAI provides a modular foundation for organizing that profile and making the relationship between a student's current skills and career requirements inspectable.

## Implemented

- FastAPI application with CORS, health check, startup database initialization, and consistent unexpected-error responses.
- SQLite persistence through SQLAlchemy 2, with Pydantic validation and separate request/response schemas.
- Student create, retrieve, and replace endpoints, including skills with proficiency, interests, academic context, and learning goals.
- Self-reported skill assessment with seeded questions, validated proficiency ratings, persisted assessment results, and student skill-profile updates.
- Career catalog, required-skill gap analysis, learning-resource suggestions, and persisted roadmaps with completion tracking.
- Explainable career comparison and non-persistent what-if simulation using the same weighted skill-ranking baseline. Scores are not ML predictions.
- Project, learning-path, sample internship, and explicitly sample-only trend catalogs.
- Career assistant with keyword retrieval over structured catalog data and source excerpts. Gemini answer generation is available through a backend-only REST adapter when configured.
- CSV catalog for 14 career paths, their required skills, learning resources, example projects, and sample-only trend placeholders. No salary or labor-demand claims are included.
- Responsive vanilla HTML/CSS/JavaScript landing page, profile dashboard, assessment, catalog, development, comparison, simulation, and assistant pages using the Fetch API.
- Unit and API tests using an isolated in-memory SQLite database.
- Modular boundaries for recommendation, skill, ML, RAG, assistant, assessment, roadmap, project, certification, internship, trend, and simulation work.

## Planned

- Adaptive knowledge-tested assessments and skill evidence from projects or coursework. The current assessment is a self-rating, not an objective skills exam.
- Trained and validated ML ranking models and semantic career matching.
- Sentence Transformer embeddings, external document ingestion, and FAISS semantic retrieval. Current retrieval uses keyword overlap over structured catalog records.
- Sourced industry trend ingestion, live internship integrations, authentication, and PostgreSQL deployment.

Internship and trend records are sample data, not live listings or labor-market statistics. Gemini generation requires a key; without it, the assistant returns retrieved sources only and labels the response retrieval-only.

## Architecture

```text
Vanilla HTML/CSS/JavaScript
          | Fetch / REST
          v
       FastAPI
          v
 API routes -> Pydantic schemas -> service layer
                                  |          |
                                  v          v
                          SQLAlchemy/SQLite  recommendation, skills,
                                             ML and RAG boundaries
```

Models, API schemas, route handlers, business services, recommendation logic, ML, RAG, and LLM provider interfaces are separate. SQLite is configured through `DATABASE_URL`; PostgreSQL can be introduced by switching the SQLAlchemy connection URL and adding its driver.

## Technology

- Frontend: HTML5, CSS3, modular vanilla JavaScript, Fetch API, Chart.js.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy.
- Initial database: SQLite.
- Test stack: pytest, HTTPX, in-memory SQLite.
- Later AI/ML options are documented in `backend/ml`, `backend/recommendation`, `backend/rag`, and `backend/ai`; large ML packages are not installed in this foundation.

## Structure

```text
frontend/       Static pages, styles, modules, and assets
backend/api/    REST route handlers
backend/schemas/ Pydantic request and response contracts
backend/services/ Business logic
backend/database/ SQLAlchemy models, engine, and sessions
backend/ml/     Feature engineering, training, evaluation, and inference boundaries
backend/recommendation/ Matching and ranking
backend/skills/ Skill normalization and gap helpers
backend/rag/    Document ingestion, chunking, embedding, and retrieval boundaries
backend/ai/     LLM provider and assistant boundaries
data/           Structured career catalog and sample content
scripts/        Database setup, catalog seeding, and future index building
tests/          API and service tests
```

## Install

Python 3.12 or newer is recommended. From the `careerai` directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Use the matching `python -m venv .venv` command if your installed Python launcher uses a different version. Catalog, assessment, comparison, and planning flows need no Gemini key.

## Database

The API creates its tables at startup. To initialize them manually and seed the career catalog:

```powershell
python -m scripts.initialize_database
python -m scripts.seed_data
```

Re-running the seed command updates the catalog without duplicating its career, skill, assessment, or sample records. Career recommendations are empty until the catalog is seeded and a student has added skills.

## Run Backend

From `careerai` with the virtual environment active:

```powershell
python -m uvicorn backend.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`  
Health: `http://127.0.0.1:8000/api/health`

## Run Frontend

In a second terminal, also from `careerai`:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500/index.html`. The frontend calls the backend at `http://127.0.0.1:8000/api`; the API key is never included in browser code.

## Docker

```powershell
docker compose up --build
```

The SQLite file is stored in the mounted `data/` directory. The API seeds the dummy catalogs on startup; `python -m scripts.seed_data` can also be run manually to refresh them.

## Render Demo Deployment

This project includes a Render Blueprint at `render.yaml`. It deploys one Docker web service that serves both the frontend and API at the same origin. On startup it creates the SQLite schema and idempotently seeds the sample catalogs. The Blueprint stores SQLite at `/tmp/careerai.db`; on Render's free service that filesystem is temporary, so demo student profiles and progress can reset after a restart or redeploy. The dummy catalog is reseeded automatically.

1. Push the `careerai` project to a GitHub repository.
2. In Render, choose **New > Blueprint**, connect that repository, and approve the Blueprint settings.
3. Wait for the deploy to pass `/api/health`, then open the `onrender.com` URL Render provides. The frontend and API share that URL, so no local API address or CORS setup is required.

Docker is not required on your computer for this Render flow; Render builds the Dockerfile remotely. No Gemini key is required for the demo features. If you later configure one, add it as a Render secret environment variable; never commit it to GitHub.

## Tests

```powershell
python -m pytest -q
```

Tests cover health, student create/read and validation, duplicate emails, SQLite schema creation, and rule-based recommendation explanations.

## AI/ML Development Path

1. Add scored knowledge checks and evidence provenance beyond self-ratings.
2. Collect consented, labeled outcomes before training and evaluating a ranking model.
3. Add versioned career documents, chunking metadata, embeddings, and a FAISS retriever with source tracking.
4. Configure and monitor Gemini generation with a server-side key and request limits.
5. Connect verified trend sources and live internship providers.
6. Add authentication, consent, and account-level data controls before production deployment.
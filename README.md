# Garmin-Buddy 🏃‍♂️📊🤖

Garmin-Buddy is a Python-based **data + AI application** that ingests my Garmin activity data, stores and models it in a relational database, computes training metrics, and uses **LLMs** to generate **actionable training insights**. It also includes a simple **data app UI** for reviewing recent activities, trends, and AI-generated summaries.

This is both:
- a **personal training companion** (analysis + planning support), and
- a **portfolio project** proving end-to-end skills in **data engineering + AI integration + cloud + product thinking**.

---

## What problem it solves

Garmin gives you lots of data, but turning it into **decisions** is harder:
- What’s the real training load trend over time?
- Am I accumulating fatigue or adapting?
- How does my intensity distribution look vs. plan?
- What should I change next week given my history?

Garmin-Buddy turns raw activity logs into:
- structured metrics and trends, and
- **context-aware AI commentary** based on my training history (not generic advice).

---

## High-level architecture

**Flow**
1. Ingest activities from Garmin (API + exported files)
2. Store raw + processed data in a relational DB (Azure SQL)
3. Compute training metrics (weekly load, intensity distribution, trends)
4. Use AI layer (LLM + retrieval) to generate insights and planning suggestions
5. Present results in a simple UI (Streamlit)

**Components**
- **Ingestion**: Garmin API / FIT parsing
- **Processing**: metrics, transformations, aggregation
- **Database**: SQLAlchemy models + migrations
- **AI Engine**: prompts + structured output + optional RAG over training history
- **UI**: Streamlit dashboard

> A diagram lives in `docs/architecture.md` (or will, if you haven’t added it yet).

---

## What this project demonstrates (for hiring)

This repository is intentionally built to demonstrate capabilities aligned to roles like:
**AI-Enabled Data Product Builder**, **AI Solutions Analyst**, **Data App Engineer**, **LLM Integrator**.

Concrete signals:
- **Data ingestion & ETL** (external data → normalized storage → analytics-ready tables)
- **Relational modeling** (SQL schema design, migrations, consistency)
- **Analytical feature engineering** (training metrics that support decisions)
- **LLM integration** (structured outputs, prompt design, reliability)
- **RAG** (injecting relevant historical context into AI reasoning)
- **Data app UI** (decision-support dashboard, not just scripts)
- **Production mindset** (config management, logging, error handling, CI-ready structure)
- **Cloud deployment** (Azure-friendly setup)

---

## Features

### Current / Core
- Garmin activity ingestion (API / FIT files)
- Storage in SQL database (Azure SQL)
- Basic computed metrics (distance, time, pace, trends)
- Initial UI (Streamlit): recent activities table + top activities views

### Planned / In progress
- Training load tracking (weekly summaries, intensity distribution)
- Fatigue / readiness indicators based on data proxies (non-medical)
- AI-generated weekly summary and training recommendations
- RAG over training history for contextual answers (“why is this week harder?”)
- Deployment + CI/CD (Docker + GitHub Actions + Azure)

---

## Project structure

```text
garmin-buddy/
├── app/
│   ├── config/          # env loading, settings, logging setup
│   ├── ingestion/       # Garmin API, FIT loading/parsing
│   ├── processing/      # transformations, metrics, aggregations
│   ├── ai/              # prompts, LLM clients, RAG, evaluations
│   ├── db/              # SQLAlchemy models, session, migrations
│   └── ui/              # Streamlit app
├── docs/                # architecture, roadmap, internal notes
├── notebooks/           # experiments only (no core logic)
├── tests/
├── .env.example
├── README.md
└── pyproject.toml
```

## Tech stack

- **Language:** Python
- **Data processing:** pandas
- **Database / ORM:** Azure SQL + SQLAlchemy
- **Ingestion:** Garmin Connect API client, FIT file parsing (e.g., `fitparse`)
- **UI:** Streamlit
- **LLM providers:** OpenAI and/or Google (configurable)
- **Embeddings / RAG:** FAISS or Chroma (optional, for retrieval)
- **Packaging / runtime:** Docker
- **CI/CD:** GitHub Actions (planned)

## Setup

### Prerequisites
- Python 3.11+ recommended
- Access to a Garmin account (for API ingestion)
- A SQL database (local or Azure SQL)
- LLM API key (OpenAI and/or Google) for AI features

### Environment variables
Copy `.env.example` → `.env` and fill in:

```bash
GARMIN_EMAIL=
GARMIN_PASSWORD=
DB_CONNECTION_STRING=
OPENAI_API_KEY=
GOOGLE_API_KEY=
FIT_DIR_PATH= 
```

> The app fails fast if required variables are missing.

## Run locally

### 1) Install dependencies
```bash
pip install -r requirements.txt
```

> (or poetry install if using Poetry)

### 2) Run the Streamlit UI
```bash
streamlit run app/ui/app.py
```

### 2) Sync activities (example)
```bash
python -m app.services.sync_service
```

> Actual command names may vary depending on your current module naming.  
> Keep scripts in `app/ingestion/` and expose a single entrypoint per action.

## AI usage notes

Garmin-Buddy provides **training insights**, not medical advice. AI outputs are:

- derived from my activity history and computed metrics,
- constrained using structured output formats where possible,
- treated as decision support, not truth.

If you implement RAG:

- the AI assistant answers using retrieved historical sessions and summaries,
- reducing hallucination risk and increasing relevance.

## Roadmap

Sprint-based plan lives in `docs/roadmap.md`.

Short version:

- **MVP:** ingestion → DB → metrics → UI → AI weekly summary
- **v0.2:** RAG + structured LLM pipelines + evaluation notebook
- **v0.3:** deployment + CI/CD + polished demo

## Screenshots / Demo

- Screenshots: add to `/docs/images/` and link here
- Demo video: add link once recorded

## Disclaimer

This project is a personal training assistant and portfolio project.  
It is not a medical tool, and nothing here should be treated as professional medical guidance.

## License
```text
TBD (MIT recommended for portfolio projects unless you have reasons to restrict usage).
```
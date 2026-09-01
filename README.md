DataBrief --- AI Analytics Platform





Upload a messy sales or inventory spreadsheet. Get computed anomaly
detection, feature-driver analysis, and an AI-written executive brief.

🔗 Live Demo: https://analytics-ai-platform.vercel.app

DataBrief is a hybrid analytics application built around one principle:

The ML models do the math. The LLM explains it.

Real machine-learning models compute the analytical evidence, while a
team of LLM agents turns those results into a business-facing executive
brief. The LLM is not responsible for inventing numerical analysis; it
is given computed evidence and constrained to explain it.

Portfolio project built to explore production-style ML + LLM system
design end to end.

Try It

Open the live demo.

Upload a CSV, Excel, or JSON file under 4 MB.

Choose a target column for driver analysis, or use auto-detect.

Select anomaly detection, driver analysis, or a full analysis.

Run the analysis and review the computed evidence and executive
brief.

No signup is required.

Why DataBrief?

A common approach to "AI-powered analytics" is to send raw spreadsheet
data to an LLM and ask it to perform the analysis.

DataBrief takes a different approach:

Data → deterministic ML computation → evidence → LLM explanation

Anomaly detection: IsolationForest plus per-column IQR bounds.

Driver analysis: XGBoost predicts a user-selected target and
reports feature importance and model quality.

LLM layer: four specialist agents explain the computed evidence
and synthesize an executive brief.

Grounding: computed evidence is injected into the agent prompts
as the source of truth.

Reliability: the system includes JSON parsing, retries,
small-file guards, ID-column exclusion, and graceful degradation.

The goal is to keep the numerical analysis defensible while using an LLM
where it is most useful: turning technical output into understandable
business language.

What It Does

1. Data ingestion

Accepts tabular:

CSV

Excel

JSON

Unsupported input is rejected with a clear error. Multi-encoding support
is included for common CSV variations.

2. Anomaly detection

Uses IsolationForest with a tuned 3% contamination rate.

The pipeline also:

excludes ID-like columns

applies per-column IQR bounds

includes a minimum-row guard

reports severity-tagged anomalies

This prevents identifiers and very small datasets from producing
misleading results.

3. Driver analysis

The user selects which column should be predicted, such as Profit or
Sales.

XGBoost then:

trains against the selected target

ranks the input features

reports feature importance

calculates R² as a model-quality signal

reports GPU/CUDA usage when available, with CPU fallback

The target can be changed from the UI, causing the driver analysis to be
recomputed.

4. Multi-agent LLM analysis

The computed ML evidence is passed to four specialist agents:

Anomaly Agent

Insight Agent

Strategy Agent

Summary Agent

An orchestrator runs the agents in parallel and synthesizes their
outputs into an executive brief.

The agents are instructed to explain the computed evidence rather than
independently calculate the numbers.

Architecture

File Upload
     │
     ▼
FastAPI Backend
     │
     ├── ML Layer — Computed Evidence
     │     ├── IsolationForest
     │     └── XGBoost
     │
     ├── Multi-Agent LLM Layer — Explanation
     │     ├── AnomalyAgent
     │     ├── InsightAgent
     │     ├── StrategyAgent
     │     ├── SummaryAgent
     │     └── Orchestrator
     │
     ▼
JSON Response
     │
     ▼
Vanilla HTML / CSS / JavaScript Frontend

The core separation is intentional:

ML computes → LLM explains → UI presents

Tech Stack

Backend

Python 3.12

FastAPI

Uvicorn

Machine Learning

scikit-learn

IsolationForest

XGBoost

pandas

NumPy

LLM

OpenRouter API

Custom multi-agent orchestration

Grounded prompting

Structured JSON output handling

Current LLM Model

liquid/lfm-2.5-2.6b:free via OpenRouter.

The model is intentionally swappable through the LLM client abstraction.

Frontend

Vanilla HTML

CSS

JavaScript

No frontend framework

No build step

Deployment

Vercel

Unified frontend + FastAPI backend

Design Decisions

Grounded generation over free generation

The LLM is not trusted to independently perform numerical analysis.

Instead:

ML computes the evidence.

The evidence is inserted into agent prompts.

Agents explain that evidence.

The resulting brief includes a verification disclaimer.

This creates a clear boundary between computed facts and generated
narrative.

User-selected prediction target

Driver analysis is only meaningful relative to a target.

The UI therefore lets the user choose the column to predict. Changing
the target causes the XGBoost analysis and displayed drivers to change.

Honest model reporting

The application reports R² so that weak predictive relationships are not
presented as strong conclusions.

It also reports whether XGBoost used GPU/CUDA or CPU execution.

Provider-agnostic LLM layer

The application wraps the OpenRouter API behind a dedicated client
interface.

This keeps the application architecture independent of a single model
provider and makes model changes straightforward.

Guards against silent nonsense

The application includes:

ID-column exclusion

tiny-file guards

supported-file validation

retry handling

JSON parsing safeguards

graceful degradation

Reliability and Known Limitations

This is a portfolio project, not a production multi-tenant analytics
platform.

LLM reliability

The current deployment uses a free-tier model. The model can
occasionally introduce an incorrect figure in the generated prose.

The computed ML evidence remains separate from that narrative, and the
brief includes a verification disclaimer.

Latency

The free LLM tier can introduce significant latency depending on
provider traffic. A run may take roughly 30 seconds to several minutes.

With a paid model and priority routing, the expected latency is lower.

File size

Hosted uploads are limited to 4 MB because of Vercel Functions'
request/response payload constraints.

Larger datasets would be better handled through durable object storage
with the analysis function receiving a file reference.

Authentication

The current application is single-user and does not implement
authentication or multi-tenancy.

Data quality

Analysis quality depends on the uploaded dataset containing meaningful
numeric columns and enough observations for the selected ML methods to
produce useful signals.

Running Locally

Clone the repository and install the dependencies:

pip install -r requirements.txt

Set your OpenRouter API key in .env:

OPENROUTER_API_KEY=your_key_here

Start the application:

uvicorn backend.main:app --reload

Then open:

http://localhost:8000

Deployment

The application is deployed as a unified Vercel project.

The deployment serves:

the frontend

the FastAPI backend

the analysis endpoints

The OPENROUTER_API_KEY should be configured as a Vercel environment
variable.

Screenshots

Analytics Overview



Computed KPIs, XGBoost feature drivers, and severity-tagged anomalies.

Executive Brief



The LLM layer explaining computed evidence, with a verification
disclaimer.

Roadmap

Data ingestion with multi-encoding support

IsolationForest anomaly detection

XGBoost driver analysis with user-selectable target

Multi-agent LLM system

Parallel agent orchestration

Vanilla JavaScript frontend

Vercel deployment

Time-series forecasting with Prophet

RAG memory for cross-session context

Authentication and multi-tenancy

Larger file support through object storage

Custom domain

Links

Live Demo: https://analytics-ai-platform.vercel.app

GitHub: https://github.com/Saras112002/Analytics-AI-Platform

LinkedIn: https://www.linkedin.com/in/saras-chawla02/

Author

Saras Chawla

Data Science student at IIT Guwahati

Built as a portfolio project to explore ML engineering, LLM
applications, backend development, and production-style AI system
design.

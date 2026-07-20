# DataBrief — AI Analytics Platform

**Upload a messy sales/inventory spreadsheet. Get computed anomaly detection, feature-driver analysis, and an AI-written executive brief — in about 20 seconds.**

DataBrief is a hybrid analytics tool built on one core idea: **the ML models do the math, the LLM explains it.** Real machine-learning models compute the hard numbers (which rows are anomalous, which columns predict a metric you choose), and a team of LLM agents translates those numbers into a business brief a manager could actually read. The AI never invents the analysis — it narrates results that were computed, not guessed.

> _Portfolio project. Built to learn production-style ML + LLM system design end to end._

---

## Why this is different

Most "AI analyzes your data" tools hand the raw spreadsheet to an LLM and hope it does the math. LLMs are bad at math and confidently make numbers up. DataBrief inverts that:

- **Computation is done by real models**, not the language model:
  - **Anomaly detection** → `IsolationForest` (scikit-learn) + per-column IQR bounds.
  - **Driver analysis** → `XGBoost` gradient boosting, GPU-accelerated when a GPU is available (CPU fallback otherwise).
- **The LLM only explains** the computed evidence. Agent prompts are constrained to cite only numbers present in the computed output, and every brief ships with a verification disclaimer.

The result: the trustworthy numbers come from deterministic ML you can defend in an interview, and the readable narrative comes from the LLM — with clear boundaries between the two.

---

## What it does

1. **Ingests** a tabular file — CSV, Excel, or JSON (non-tabular input is rejected with a clear message).
2. **Computes anomalies** with IsolationForest at a tuned 3% contamination rate, excluding ID-like columns so identifiers aren't mistaken for outliers, with a minimum-rows guard so tiny files don't report meaningless rates.
3. **Ranks drivers** with XGBoost. **You choose which column to predict** (e.g. Profit, Sales) from a dropdown, or let it auto-detect. It reports which features predict your target and how strongly, plus an honest model-quality score (R²) so weak models are flagged as weak.
4. **Runs a multi-agent LLM layer** — four specialist agents (anomaly, insight, strategy, summary) coordinated by an orchestrator — that synthesizes the computed evidence into an executive brief with recommended actions.
5. **Renders** everything in a clean terminal-style UI: KPI cards, an animated driver bar chart that re-ranks when you change the target, severity-tagged anomalies, and the brief.

You also choose *which* analyses to run (anomalies, drivers, or a full pass) — the UI passes those choices to the backend so only the requested computation runs.

---

## Architecture

```
File upload
   │
   ▼
FastAPI backend
   │
   ├── ML layer (the computed truth)
   │     ├── IsolationForest  → anomaly evidence
   │     └── XGBoost          → driver evidence (user-selected target)
   │
   ├── Multi-agent LLM layer (the explanation)
   │     ├── BaseAgent  →  AnomalyAgent · InsightAgent · StrategyAgent · SummaryAgent
   │     └── Orchestrator (parallel execution → synthesized brief)
   │
   ▼
JSON response  →  vanilla HTML/JS frontend (DataBrief)
```

The ML evidence is injected into each agent's prompt as ground truth. Agents explain that evidence; they do not compute it.

---

## Tech stack

- **Backend:** Python 3.12, FastAPI, Uvicorn
- **ML:** scikit-learn (IsolationForest), XGBoost (GPU/CUDA with CPU fallback), pandas, NumPy
- **LLM:** OpenRouter API (model-agnostic), custom multi-agent orchestration with grounded prompting
- **Frontend:** vanilla HTML / CSS / JavaScript — no framework, no build step
- **Reliability:** hardened JSON parsing, request retries, graceful degradation on missing/tiny data

---

## Running locally

You need two terminals: one for the API, one to serve the page.

**1. Backend** (from the project root):
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Set your `OPENROUTER_API_KEY` in a `.env` file first.

**2. Frontend** (from the `frontend/` folder):
```bash
python -m http.server 5500
```
Then open **http://localhost:5500/signal.html**, choose a file, pick a target column (or leave it on auto), and press RUN.

---

## Design decisions worth noting

- **Grounded generation over free generation.** Rather than trusting the LLM to be accurate, the system computes evidence first and constrains the LLM to explain only that evidence — with a disclaimer for the residual gap. This is the honest way to use LLMs on numeric data.
- **The user picks the target.** Driver analysis is only meaningful against a chosen target, so the UI lets the analyst select which column to predict and re-runs XGBoost against it — the drivers visibly change with the choice.
- **Honest model reporting.** XGBoost reports whether it actually ran on GPU vs. CPU, and reports its own R² so a weak model is labeled "weak signal" instead of being presented as fact.
- **Guards against silent nonsense.** ID columns are excluded from ML, tiny files are refused, and unsupported file types return clear errors instead of crashing.

---

## Honest limitations

This is a portfolio project, not a production system:

- It runs on a **free LLM tier**, which occasionally fabricates a figure inside the prose narrative. This is why every brief carries a verification disclaimer — the computed evidence (anomalies, driver importances, model quality) is reliable; the AI's surrounding prose should be checked.
- **Single-user, no authentication.**
- Analysis quality depends on the uploaded data having meaningful numeric columns.

These are known and deliberate scope choices, not oversights.

---

## Author

Built by **[Your Name]** — [GitHub](https://github.com/Saras112002/Analytics-AI-Platform) · [LinkedIn](#)

_Add a screenshot of the DataBrief UI here — it's the fastest way to show it works._
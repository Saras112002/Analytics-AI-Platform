# AI Analytics Platform

An AI-powered business analytics platform that ingests datasets and generates consultant-level insights through a multi-agent AI system. Built with FastAPI, Pandas, and a provider-agnostic LLM architecture.

## Features

- **Smart File Ingestion** — Multi-encoding CSV/Excel support with automatic schema detection
- **Multi-Agent AI System** — 4 specialized AI agents working together like a consulting team
- **Provider-Agnostic LLM** — Wrapper pattern supports OpenRouter, Claude, OpenAI
- **Production Patterns** — Async endpoints, base class inheritance, defensive error handling
- **Structured Prompt Engineering** — Calibrated outputs with confidence levels and severity scoring
- **Auto API Documentation** — Interactive OpenAPI docs at /docs

## Multi-Agent Architecture

The system uses specialized AI agents working in concert:

| Agent | Role | Output |
|-------|------|--------|
| **InsightAgent** | Senior business analyst | General observations, patterns, suggested analyses |
| **AnomalyAgent** | Forensic data scientist | Outliers, data quality issues, severity scores |
| **StrategyAgent** | McKinsey consultant | Strategic recommendations with ROI reasoning |
| **SummaryAgent** | Chief Strategy Officer | Executive brief synthesizing all findings |

All agents inherit from a `BaseAgent` class providing shared LLM communication, JSON parsing, and prompt building — keeping the codebase DRY and extensible.

### Example: Strategy Agent Output

```json
{
  "recommendation": "Implement Tiered Loyalty pricing model",
  "reasoning": "8,500 orders from 1,200 customers = 7x frequency",
  "data_evidence": "customer_id (1,200 unique) vs order_id (8,500 unique)",
  "effort": "medium",
  "impact": "high",
  "confidence": "high",
  "cheap_test": "2-week A/B test on top 10% customers",
  "success_metric": "AOV increase, discount_percent reduction"
}
```

### Example: Executive Summary Output

```json
{
  "headline": "Customer concentration risk - 7x order frequency from limited base signals revenue vulnerability",
  "top_actions": [
    {
      "action": "Launch tiered loyalty program",
      "why_now": "Protects margins while retaining top customers",
      "expected_outcome": "5-10% LTV increase within 6 months"
    }
  ],
  "bottom_line": "Shift from broad discounting to loyalty incentives. This protects margins and increases overall LTV.",
  "decision_required": "Should we approve $50K pilot for tiered loyalty program in Q3?"
}
```

## Architecture
analytics-ai/

├── backend/

│   ├── agents/

│   │   ├── base_agent.py        # Parent class for all agents

│   │   ├── insight_agent.py     # Business analysis

│   │   ├── anomaly_agent.py     # Outlier detection

│   │   ├── strategy_agent.py    # Strategic recommendations

│   │   └── summary_agent.py     # Executive synthesis

│   ├── api/

│   │   ├── upload.py            # File ingestion endpoint

│   │   └── analyze.py           # AI analysis endpoint

│   ├── pipelines/

│   │   └── file_processor.py    # Data processing logic

│   ├── tools/

│   │   └── llm_client.py        # Provider-agnostic LLM wrapper

│   ├── memory/                  # Future: RAG and memory

│   ├── config.py                # App configuration

│   └── main.py                  # Entry point

├── data/uploads/                # User uploaded files

├── requirements.txt

└── README.md

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and app info |
| GET | `/health` | System health status |
| POST | `/api/upload` | Upload CSV/Excel for analysis |
| POST | `/api/analyze` | Generate AI insights on uploaded file |

## Getting Started

### Prerequisites

- Python 3.10+
- OpenRouter API key (free tier available at openrouter.ai)

### Installation

```bash
# Clone the repository
git clone https://github.com/Saras112002/Analytics-AI-Platform.git
cd Analytics-AI-Platform

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create a .env file with:
OPENROUTER_API_KEY=your-key-here

# Run the server
uvicorn backend.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## How It Works

### 1. Data Ingestion

Files are uploaded via `POST /api/upload`. The system:
- Validates file type and size (max 50MB)
- Tries multiple text encodings (UTF-8, Latin-1, CP1252) for real-world compatibility
- Extracts schema automatically using Pandas
- Returns structured summary with dtypes, null percentages, unique counts, and sample values

### 2. AI Analysis

Calling `POST /api/analyze` with a filename triggers the multi-agent pipeline:

1. **InsightAgent** examines the schema and generates observations
2. **AnomalyAgent** scans for outliers, data quality issues, and red flags
3. **StrategyAgent** translates findings into actionable business recommendations
4. **SummaryAgent** synthesizes everything into a 5-minute executive brief

### 3. Structured Output

Every agent returns calibrated JSON:
- Confidence levels (high/medium/low) prevent false certainty
- Severity scoring (high/medium/low) prioritizes attention
- Specific column references ground recommendations in actual data
- Cheap tests are suggested before big investments

## Engineering Patterns Used

- **Inheritance** — All agents extend `BaseAgent` for shared functionality
- **Method Overriding** — `SummaryAgent` overrides `analyze()` for different input type
- **Wrapper Pattern** — LLM client abstracts provider details for easy swapping
- **Dependency Injection** — Settings loaded via `pydantic-settings` and injected
- **Defensive Programming** — All LLM responses validated before parsing
- **Async/Await** — Non-blocking file uploads and AI calls

## Roadmap

- [x] **Phase 1-3** — Foundation, FastAPI backend, data ingestion
- [x] **Phase 4** — AI/LLM integration with provider-agnostic wrapper
- [x] **Phase 5** — Multi-agent system (Insight, Anomaly, Strategy, Summary agents)
- [ ] **Phase 6** — ML model integration (XGBoost, Prophet, Isolation Forest)
- [ ] **Phase 7** — Auto-generated dashboards and visualizations
- [ ] **Phase 8** — RAG memory for cross-session context
- [ ] **Phase 9** — React frontend
- [ ] **Phase 10** — Multi-tenant SaaS architecture
- [ ] **Phase 11** — Production deployment and scaling

## Status

Active development. **5 of 11 phases complete.** Currently working on agent orchestration and ML model integration.

## Author

**Saras Chawla** — Data Science student at IIT Guwahati

GitHub: [@Saras112002](https://github.com/Saras112002)
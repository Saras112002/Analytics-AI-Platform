#
Then open **<http://localhost:8000>**, choose a file, pick a target column (or leave it on auto), and press RUN.

### Deploying to Vercel

Deploy the repository root (the directory containing `app.py` and `requirements.txt`) and add `OPENROUTER_API_KEY` in **Project Settings → Environment Variables**. The frontend and FastAPI backend are served from the same Vercel deployment, so no separate API URL is required.

Uploads are limited to 4 MB because Vercel Functions enforce a 4.5 MB request and response payload limit. Analysis is performed from the multipart upload in a single invocation; uploaded workbooks are not stored on the function's local filesystem.

---

## Design decisions worth noting

- **Grounded generation over free generation.** Rather than trusting the LLM to be accurate, the system computes evidence first and constrains the LLM to explain only that evidence — with a disclaimer for the residual gap. This is the honest way to use LLMs on numeric data.
- **The user picks the target.** Driver analysis is only meaningful against a chosen target, so the UI lets the analyst select which column to predict and re-runs XGBoost against it — the drivers visibly change with the choice.
- **Honest model reporting.** XGBoost reports whether it actually ran on GPU vs. CPU, and reports its own R² so a weak model is labeled "weak signal" instead of being presented as fact.
- **Provider-agnostic LLM wrapper.** The LLM client abstracts OpenRouter behind a clean interface. Swapping to Claude, GPT, or a self-hosted model requires changing one file.
- **Guards against silent nonsense.** ID columns are excluded from ML, tiny files are refused, and unsupported file types return clear errors instead of crashing.

---

## Honest limitations

This is a portfolio project, not a production system:

- It runs on a **free LLM tier**, which occasionally fabricates a figure inside the prose narrative. This is why every brief carries a verification disclaimer — the computed evidence (anomalies, driver importances, model quality) is reliable; the AI's surrounding prose should be checked.
- **Analysis latency depends on the free LLM tier.** Response times vary with traffic on the free model pool; a run may take anywhere from ~30s to a couple of minutes. On a paid model with priority routing this drops to roughly 20 seconds. The bottleneck is the hosted model's throughput, not the computation.
- **Hosted uploads are capped at 4 MB.** This keeps multipart requests below Vercel's function payload limit. Larger datasets should be uploaded directly to durable object storage and passed to the analysis function by reference.
- **Single-user, no authentication.** Multi-tenancy and auth are planned but not implemented.
- **Analysis quality depends on the uploaded data** having meaningful numeric columns and enough rows for ML to be statistically valid.

These are known and deliberate scope choices, not oversights.

---

## Screenshots

[![DataBrief analysing a retail dataset](https://github.com/Saras112002/Analytics-AI-Platform/raw/main/screenshots/databrief-overview.png)](/Saras112002/Analytics-AI-Platform/blob/main/screenshots/databrief-overview.png)
*Computed KPIs, XGBoost feature drivers, and severity-tagged anomalies.*

[![Executive brief](https://github.com/Saras112002/Analytics-AI-Platform/raw/main/screenshots/databrief-brief.png)](/Saras112002/Analytics-AI-Platform/blob/main/screenshots/databrief-brief.png)
*The LLM layer explaining the computed evidence, with its verification disclaimer.*

---

## Roadmap

- [x] Data ingestion with multi-encoding support
- [x] IsolationForest anomaly detection with tuned contamination rate
- [x] XGBoost driver analysis with user-selectable target
- [x] Multi-agent LLM system (Anomaly, Insight, Strategy, Summary agents)
- [x] Parallel agent orchestration
- [x] Vanilla JS frontend with reactive updates
- [x] Vercel deployment (full-stack unified)
- [ ] Time-series forecasting with Prophet
- [ ] RAG memory for cross-session context
- [ ] User authentication and multi-tenancy
- [ ] Larger file support via object storage
- [ ] Custom domain

---

## Author

Built by **Saras Chawla** — Data Science student at IIT Guwahati

- GitHub: [@Saras112002](https://github.com/Saras112002)
- LinkedIn: [saras-chawla02](https://www.linkedin.com/in/saras-chawla02/)
- Live Project: [analytics-ai-platform.vercel.app](https://analytics-ai-platform.vercel.app)

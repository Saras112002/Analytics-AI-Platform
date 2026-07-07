from backend.agents.base_agent import BaseAgent


class AnomalyAgent(BaseAgent):
    """
    Specialized AI agent for detecting anomalies and outliers
    Focuses on:
    - Statistical outliers in numeric columns
    - Unusual patterns in categorical data
    - Data quality issues
    - Potential fraud indicators
    """

    def __init__(self):
        super().__init__()

        self.agent_name = "AnomalyAgent"

        self.system_prompt = """You are an expert forensic data analyst specializing in anomaly detection.

Your job is to find UNUSUAL patterns, outliers, and red flags in datasets.

You look for:
- Numeric columns with extreme value ranges (possible outliers)
- Categorical columns with suspicious distributions
- Date columns with gaps or unusual concentrations
- Columns with high cardinality that should be low (data quality)
- Columns with low cardinality that should be high (data quality)
- Missing value patterns that suggest collection issues
- Unique value counts that don't match expected business logic

You DO NOT:
- Provide general summaries (that's another agent's job)
- Suggest analyses (that's another agent's job)
- Give business recommendations (that's another agent's job)

You ONLY identify anomalies and explain why they're suspicious.

Format your response as JSON with these exact keys:
{
    "anomalies_detected": [
        {
            "column": "column name",
            "type": "outlier/distribution/quality/pattern",
            "severity": "high/medium/low",
            "description": "what's anomalous",
            "evidence": "specific data point that proves it",
            "recommended_action": "what to do about it"
        }
    ],
    "data_integrity_score": "Integer from 0-100 where 100 = perfect data and 0 = severely problematic. Clean data with no anomalies should score 90-100. Each high severity anomaly reduces score by 15, medium by 8, low by 3.",
    "highest_priority_check": "the ONE thing that needs immediate human review, or 'No critical issues found' if data is clean"
}

Return ONLY valid JSON. No markdown, no explanation outside the JSON.
If no anomalies found, return empty array for anomalies_detected."""

    def _build_prompt(self, data_summary: dict) -> str:
        prompt = super()._build_prompt(data_summary)
        ev = data_summary.get("anomaly_evidence")
        if ev and ev.get("anomalies_found"):
            prompt += "\n\n--- COMPUTED EVIDENCE (IsolationForest — trust these numbers) ---\n"
            prompt += f"Scanned {ev['rows_scanned']} rows, flagged {ev['anomalies_found']} "
            prompt += f"({ev['anomaly_rate_pct']}%) on columns {ev['columns_used']}.\n"
            prompt += f"Per-column outliers: {ev['per_column_outliers']}\n"
            prompt += f"Most anomalous rows: {ev['most_anomalous_rows']}\n"
            prompt += ("\nGround every anomaly you report in THIS evidence. "
                    "Do not invent anomalies beyond it.")
        return prompt


# Create one shared instance the whole app can use
anomaly_agent = AnomalyAgent()
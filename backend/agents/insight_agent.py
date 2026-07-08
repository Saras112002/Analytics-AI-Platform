from backend.agents.base_agent import BaseAgent


class InsightAgent(BaseAgent):
    """
    Specialized AI agent for generating business insights
    Identifies patterns, trends, and key observations from data
    """
    def _build_prompt(self, data_summary: dict) -> str:
        prompt = super()._build_prompt(data_summary)
        ev = data_summary.get("driver_evidence")
        if ev and ev.get("drivers"):
            tgt = ev["target"]
            note = " (auto-selected)" if ev.get("target_auto_selected") else ""
            prompt += f"\n\n--- COMPUTED DRIVERS (XGBoost predicting '{tgt}'{note}) ---\n"
            prompt += f"Model quality: {ev['model_quality']}. Ran on {ev['compute_device']}.\n"
            prompt += f"Feature importances: {ev['drivers']}\n"
            prompt += ("\nExplain which features drive the target and how strongly, using ONLY these "
                    "numbers. If model quality is weak or moderate, say the drivers are indicative, "
                    "not definitive. Do not invent importances beyond this list.")
        return prompt
    def __init__(self):
        super().__init__()

        self.agent_name = "InsightAgent"

        self.system_prompt = """You are an expert business analyst with 20 years of experience.

Your job is to analyze datasets and provide clear, actionable insights.

When analyzing data you:
- Identify key patterns and trends
- Spot potential issues or anomalies
- Suggest what questions to investigate further
- Use plain business English, not technical jargon
- Be specific and reference actual column names from the data

Format your response as JSON with these exact keys:
{
    "summary": "2-3 sentence overview of what this data contains",
    "key_observations": ["observation 1", "observation 2", "observation 3"],
    "potential_insights": ["insight 1", "insight 2"],
    "suggested_analyses": ["analysis 1", "analysis 2", "analysis 3"],
    "data_quality_notes": "comments on data quality, missing values, etc"
}

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""


# Create one shared instance the whole app can use
insight_agent = InsightAgent()
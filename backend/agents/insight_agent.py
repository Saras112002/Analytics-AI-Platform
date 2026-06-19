import json
from backend.tools.llm_client import llm


class InsightAgent:
    """
    AI agent specialized in analyzing business data
    Takes a data summary and returns insights like a consultant
    """

    def __init__(self):
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

    def analyze(self, data_summary: dict) -> dict:
        """
        Takes a data summary (from Phase 3) and returns AI insights
        """
        # Build a clear prompt from the data summary
        prompt = self._build_prompt(data_summary)

        # Ask the LLM
        response = llm.ask(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        # Parse the response as JSON
        insights = self._parse_response(response)

        return insights

    def _build_prompt(self, data_summary: dict) -> str:
        """
        Converts the data summary dict into a readable prompt
        """
        prompt = f"""Please analyze this dataset:

DATASET: {data_summary.get('filename', 'unknown')}
ROWS: {data_summary.get('rows', 0):,}
COLUMNS: {data_summary.get('columns', 0)}

COLUMN DETAILS:
"""

        schema = data_summary.get('schema', {})
        for col_name, col_info in schema.items():
            prompt += f"\n- {col_name}:"
            prompt += f"\n    Type: {col_info.get('dtype', 'unknown')}"
            prompt += f"\n    Unique values: {col_info.get('unique_values', 0)}"
            prompt += f"\n    Missing: {col_info.get('null_percentage', 0)}%"
            samples = col_info.get('sample_values', [])
            if samples:
                prompt += f"\n    Examples: {samples}"

        prompt += "\n\nProvide your analysis as JSON only."
        return prompt

    def _parse_response(self, response: str) -> dict:
        """
        Safely parses the LLM's JSON response
        Handles cases where LLM adds extra text
        """
        # Try to find JSON in the response
        try:
            # Remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                # Remove ```json or ``` from start
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
                # Remove ``` from end
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]

            insights = json.loads(cleaned)
            return insights

        except json.JSONDecodeError:
            # If parsing fails, return raw text in a safe structure
            return {
                "summary": "Could not parse AI response as JSON",
                "raw_response": response,
                "error": "JSON parsing failed"
            }


# Create one shared instance the whole app can use
insight_agent = InsightAgent()
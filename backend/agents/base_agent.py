import json
from urllib import response
from backend.tools.llm_client import llm


class BaseAgent:
    """
    Parent class for all AI agents in the system
    Provides shared functionality:
    - LLM communication
    - JSON response parsing
    - Prompt building from data summaries
    - Error handling
    
    Child agents only need to define their:
    - System prompt (their personality/role)
    - Output schema (what JSON keys they return)
    """

    def __init__(self):
        # Each child agent must override these
        self.agent_name = "BaseAgent"
        self.system_prompt = ""
        self.output_keys = []

    def analyze(self, data_summary: dict) -> dict:
        """
        Main entry point - same for all agents
        Takes data summary, returns structured insights
        """
        if not self.system_prompt:
            raise ValueError(
                f"{self.agent_name} has no system_prompt defined"
            )

        prompt = self._build_prompt(data_summary)
        response = llm.ask(
            prompt=prompt,
            system_prompt=self.system_prompt
        )
        result = self._parse_response(response)

        # Add metadata so we know which agent produced this
        result["_agent"] = self.agent_name
        return result

    def _build_prompt(self, data_summary: dict) -> str:
        """
        Converts data summary dict into a readable prompt
        Same for all agents
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
            if samples := col_info.get('sample_values', []):
                prompt += f"\n    Examples: {samples}"

        prompt += "\n\nProvide your analysis as JSON only."
        return prompt

    def _parse_response(self, response: str) -> dict:
        if response is None:
            return {
                "error": "LLM returned no response",
                "raw_response": None,
                "agent_name": self.agent_name
        }
    
        if not isinstance(response, str) or not response.strip():
            return {
                "error": "LLM returned empty or invalid response",
                "raw_response": (response),
                "agent_name": self.agent_name
        }
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]

            return json.loads(cleaned)

        except json.JSONDecodeError:
            return {
                "error": "JSON parsing failed",
                "raw_response": response,
                "agent_name": self.agent_name
            }
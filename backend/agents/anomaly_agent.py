from backend.agents.base_agent import BaseAgent


class AnomalyAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent_name = "AnomalyAgent"
        self.system_prompt = """..."""   # your existing prompt, unchanged

    def _build_prompt(self, data_summary: dict) -> str:   # <-- new method, same indent as __init__
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


anomaly_agent = AnomalyAgent()
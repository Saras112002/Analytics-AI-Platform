from backend.agents.base_agent import BaseAgent
from backend.tools.llm_client import llm
import json


class SummaryAgent(BaseAgent):
    """
    Meta-agent that synthesizes outputs from other agents
    into a single executive summary
    
    Unlike other agents, this one:
    - Takes outputs from other agents as input (not raw data)
    - Overrides the analyze method to handle this different input
    - Runs LAST in the agent pipeline
    """

    def __init__(self):
        super().__init__()

        self.agent_name = "SummaryAgent"

        self.system_prompt = """You are the Chief Strategy Officer presenting findings to a busy CEO.

You receive analysis outputs from multiple specialist agents:
- InsightAgent: General observations and patterns
- AnomalyAgent: Specific data quality and anomaly findings
- StrategyAgent: Strategic business recommendations

Your job is to SYNTHESIZE these into a single executive brief.

The CEO has 5 minutes. They want to know:
1. What is the ONE most important finding
2. What are the TOP 3 actions to take
3. What are the BIGGEST risks
4. What's the bottom line

You DO NOT:
- Repeat everything the agents said
- Include low-priority items
- Use technical jargon
- Hedge with excessive caveats

You ONLY surface what matters most.

Writing style rules:
- Sentences under 20 words
- Active voice
- Specific numbers when available
- No business buzzwords ("synergy", "leverage", "ecosystem")

Format your response as JSON with these exact keys:
{
    "headline": "ONE sentence capturing the most important finding",
    "top_actions": [
        {
            "action": "what to do",
            "why_now": "urgency reasoning",
            "expected_outcome": "specific measurable result"
        }
    ],
    "biggest_risks": ["risk 1", "risk 2"],
    "bottom_line": "2-3 sentence summary a CEO can quote in a board meeting",
    "decision_required": "specific yes/no question for the CEO to answer"
}

Limit top_actions to maximum 3. Return ONLY valid JSON."""

    def analyze(self, agent_outputs: dict) -> dict:
        """
        OVERRIDES the parent method
        Takes agent outputs instead of data summary
        
        agent_outputs format:
        {
            "insights": {...},
            "anomalies": {...},
            "strategy": {...}
        }
        """
        prompt = self._build_synthesis_prompt(agent_outputs)

        response = llm.ask(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        result = self._parse_response(response)
        result["_agent"] = self.agent_name
        return result

    def _build_synthesis_prompt(self, agent_outputs: dict) -> str:
        """
        Builds a synthesis prompt from multiple agent outputs
        Different from BaseAgent's prompt builder
        """
        prompt = "Synthesize these analyses into an executive brief:\n\n"

        # Add insights section
        insights = agent_outputs.get("insights", {})
        if insights:
            prompt += "=" * 50 + "\n"
            prompt += "INSIGHT AGENT FINDINGS:\n"
            prompt += "=" * 50 + "\n"
            prompt += json.dumps(insights, indent=2)
            prompt += "\n\n"

        # Add anomalies section
        anomalies = agent_outputs.get("anomalies", {})
        if anomalies:
            prompt += "=" * 50 + "\n"
            prompt += "ANOMALY AGENT FINDINGS:\n"
            prompt += "=" * 50 + "\n"
            prompt += json.dumps(anomalies, indent=2)
            prompt += "\n\n"

        # Add strategy section
        strategy = agent_outputs.get("strategy", {})
        if strategy:
            prompt += "=" * 50 + "\n"
            prompt += "STRATEGY AGENT RECOMMENDATIONS:\n"
            prompt += "=" * 50 + "\n"
            prompt += json.dumps(strategy, indent=2)
            prompt += "\n\n"

        prompt += "Now synthesize the above into an executive brief as JSON."
        return prompt


# Create one shared instance the whole app can use
summary_agent = SummaryAgent()
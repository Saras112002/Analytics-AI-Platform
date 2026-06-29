import asyncio
from concurrent.futures import ThreadPoolExecutor
from backend.agents.insight_agent import insight_agent
from backend.agents.anomaly_agent import anomaly_agent
from backend.agents.strategy_agent import strategy_agent
from backend.agents.summary_agent import summary_agent


class Orchestrator:
    """
    Coordinates all AI agents to produce a complete analysis
    
    Workflow:
    1. Run 3 specialist agents in PARALLEL (faster)
    2. Wait for all 3 to finish
    3. Feed their outputs to SummaryAgent
    4. Return everything bundled
    """

    def __init__(self):
        self.specialist_agents = {
            "insights": insight_agent,
            "anomalies": anomaly_agent,
            "strategy": strategy_agent
        }
        self.summary_agent = summary_agent

    def run(self, data_summary: dict) -> dict:
        """
        Main entry point - runs the full agent pipeline
        Returns combined output from all agents
        """
        # Phase 1: Run specialists in parallel
        specialist_results = self._run_specialists_parallel(data_summary)

        # Phase 2: Synthesize with summary agent
        executive_brief = self.summary_agent.analyze(specialist_results)

        # Phase 3: Bundle everything together
        return {
            "executive_brief": executive_brief,
            "detailed_findings": specialist_results,
            "agents_used": list(specialist_results.keys()) + ["summary"]
        }

    def _run_specialists_parallel(self, data_summary: dict) -> dict:
        """
        Runs all specialist agents at the same time
        Uses ThreadPoolExecutor for parallel execution
        """
        results = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all agent tasks
            future_to_name = {
                executor.submit(agent.analyze, data_summary): name
                for name, agent in self.specialist_agents.items()
            }

            # Collect results as they complete
            for future in future_to_name:
                name = future_to_name[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = {
                        "error": str(e),
                        "agent_name": name
                    }

        return results


# Create one shared instance the whole app can use
orchestrator = Orchestrator()
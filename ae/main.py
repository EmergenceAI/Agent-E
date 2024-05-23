import asyncio

from ae.core.system_orchestrator import SystemOrchestrator

if __name__ == "__main__":
    orchestrator = SystemOrchestrator(agent_scenario="user,planner_agent,browser_nav_agent,browser_nav_executor",input_mode="GUI_ONLY")
    asyncio.run(orchestrator.start())

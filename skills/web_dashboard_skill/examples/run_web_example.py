from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.web_dashboard_skill.implementation import WebDashboardSkill


def main():
    orch = SystemOrchestrator()
    web = WebDashboardSkill(orchestrator=orch)
    print("[WebDashboardSkill] Initialized Flask server. To run live, call web.run(port=5000)")


if __name__ == "__main__":
    main()

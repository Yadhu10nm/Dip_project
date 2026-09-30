import os
import config
from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.web_dashboard_skill.implementation import WebDashboardSkill

# Shared orchestrator and web skill instances
orchestrator = SystemOrchestrator()
web_skill = WebDashboardSkill(
    orchestrator=orchestrator,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)
app = web_skill.app


def run_server(host="0.0.0.0", port=5000, debug=False):
    """Launches web surveillance dashboard."""
    web_skill.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server()

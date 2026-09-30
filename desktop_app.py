from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.desktop_ui_skill.implementation import DesktopUISkill


def run_desktop_app():
    """
    Master entry point for standalone desktop CCTV application.
    Driven by SystemOrchestrator and DesktopUISkill.
    """
    orchestrator = SystemOrchestrator()
    desktop_ui = DesktopUISkill(orchestrator=orchestrator)
    desktop_ui.run()


if __name__ == "__main__":
    run_desktop_app()

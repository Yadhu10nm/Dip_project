from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.desktop_ui_skill.implementation import DesktopUISkill


def main():
    orch = SystemOrchestrator()
    desktop = DesktopUISkill(orchestrator=orch)
    print("[DesktopUISkill] Initialized OpenCV UI. To launch live interactive window, call desktop.run()")


if __name__ == "__main__":
    main()

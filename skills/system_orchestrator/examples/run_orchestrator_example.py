from skills.system_orchestrator.implementation import SystemOrchestrator


def main():
    orchestrator = SystemOrchestrator()
    print("[SystemOrchestrator] Starting cycle...")
    frame, recs, loc = orchestrator.process_cycle()
    print(f"[SystemOrchestrator] Processed frame: shape={frame.shape}, recognitions={len(recs)}, loc={loc}")
    status = orchestrator.get_status()
    print(f"[SystemOrchestrator] System Status: {status}")
    orchestrator.stop()


if __name__ == "__main__":
    main()

from skills.alert_skill.implementation import AlertSkill
from skills.common.types import RecognitionResult


def main():
    alerter = AlertSkill(cooldown_seconds=3.0)
    fake_recs = [
        RecognitionResult(name="Unknown", person_id="", similarity=0.3, authorized=False, bbox=(50, 50, 60, 60))
    ]
    evt = alerter.evaluate_detections(fake_recs)
    print(f"[AlertSkill] Evaluated event: {evt.to_dict() if evt else None}")


if __name__ == "__main__":
    main()

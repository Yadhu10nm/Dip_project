from skills.person_locator_skill.implementation import PersonLocatorSkill
from skills.common.types import RecognitionResult


def main():
    locator = PersonLocatorSkill(target_person="Yadhu")
    dummy_results = [
        RecognitionResult(name="Yadhu", person_id="u_01", similarity=0.91, authorized=True, bbox=(120, 80, 100, 100))
    ]
    loc = locator.locate_in_detections(dummy_results)
    print(f"[PersonLocatorSkill] Location: {loc.to_dict()}")


if __name__ == "__main__":
    main()

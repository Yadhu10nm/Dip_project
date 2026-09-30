import numpy as np
from skills.surveillance_skill.implementation import SurveillanceSkill


def main():
    surveillance = SurveillanceSkill()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    results = surveillance.process_frame(frame)
    print(f"[SurveillanceSkill] Processed results count: {len(results)}")


if __name__ == "__main__":
    main()

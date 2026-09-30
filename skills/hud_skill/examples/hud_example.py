import numpy as np
from skills.hud_skill.implementation import HUDSkill
from skills.common.types import RecognitionResult


def main():
    hud = HUDSkill()
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    recs = [
        RecognitionResult(name="Amith", person_id="a1", similarity=0.92, authorized=True, bbox=(60, 60, 100, 100))
    ]
    rendered = hud.render(canvas, recs, fps=30.0)
    print(f"[HUDSkill] Rendered test frame shape: {rendered.shape}")


if __name__ == "__main__":
    main()

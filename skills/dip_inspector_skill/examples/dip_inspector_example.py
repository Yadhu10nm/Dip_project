import numpy as np
from skills.dip_inspector_skill.implementation import DIPInspectorSkill


def main():
    inspector = DIPInspectorSkill()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    quad = inspector.create_quad_view(frame)
    print(f"[DIPInspectorSkill] Created quad inspection view of shape: {quad.shape}")


if __name__ == "__main__":
    main()

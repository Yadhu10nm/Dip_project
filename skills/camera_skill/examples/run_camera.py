from skills.camera_skill.implementation import CameraSkill


def main():
    camera = CameraSkill(camera_index=0)
    print("[CameraSkill] Starting camera...")
    opened = camera.start()
    print(f"[CameraSkill] Opened: {opened}")

    ret, frame = camera.get_frame()
    print(f"[CameraSkill] Frame captured: success={ret}, shape={frame.shape if frame is not None else None}")
    camera.stop()
    print("[CameraSkill] Camera stopped safely.")


if __name__ == "__main__":
    main()

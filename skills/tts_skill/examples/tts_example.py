import time
from skills.tts_skill.implementation import TTSSkill


def main():
    tts = TTSSkill()
    print("[TTSSkill] Speaking test utterance...")
    tts.speak("Security surveillance system operational.")
    time.sleep(1.0)
    tts.stop()


if __name__ == "__main__":
    main()

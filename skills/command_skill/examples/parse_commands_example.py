from skills.command_skill.implementation import CommandSkill


def main():
    skill = CommandSkill()
    samples = [
        "locate Yadhu",
        "find Bob",
        "show DIP mode",
        "disable sound",
        "stop locating"
    ]
    for s in samples:
        cmd = skill.parse(s)
        print(f"Input: '{s}' -> Command: {cmd}")


if __name__ == "__main__":
    main()

import re
from typing import Optional
from skills.common.types import Command


class CommandSkill:
    """
    Natural Language Command Parser Skill.
    Parses operator voice or text commands into structured Command objects.

    RULE:
    Does NOT directly manipulate camera, database, or alert systems.
    Outputs structured commands for the system orchestrator.
    """

    def parse(self, text: str) -> Optional[Command]:
        """Parses a natural-language query into a structured Command."""
        if not text or not text.strip():
            return None

        clean_text = text.strip()
        lower = clean_text.lower()

        # 1. Stop locating
        if re.search(r"\b(stop locating|cancel locating|clear target|stop search)\b", lower):
            return Command(type="STOP_LOCATING")

        # 2. Locate / Find Person
        match = re.search(r"\b(?:locate|find|where is|track)\s+([a-zA-Z0-9_\s]+)", clean_text, re.IGNORECASE)
        if match:
            target = match.group(1).strip()
            # Clean trailing question marks or punctuation
            target = re.sub(r"[?!.]", "", target).strip()
            if target:
                return Command(type="LOCATE_PERSON", target=target)

        # 3. Register / Enroll Person
        match = re.search(r"\b(?:register|enroll|add user|add person)\s+([a-zA-Z0-9_\s]+)", clean_text, re.IGNORECASE)
        if match:
            target = match.group(1).strip()
            target = re.sub(r"[?!.]", "", target).strip()
            if target:
                return Command(type="ENROLL_PERSON", target=target)

        # 4. DIP mode toggles
        if re.search(r"\b(?:show dip|enable dip|toggle dip|dip mode|dip inspector)\b", lower):
            return Command(type="TOGGLE_DIP")

        # 5. Sound toggles
        if re.search(r"\b(?:enable sound|unmute|turn sound on|sound on)\b", lower):
            return Command(type="TOGGLE_SOUND", params={"enabled": True})
        if re.search(r"\b(?:disable sound|mute|turn sound off|sound off)\b", lower):
            return Command(type="TOGGLE_SOUND", params={"enabled": False})
        if re.search(r"\b(?:toggle sound|switch sound)\b", lower):
            return Command(type="TOGGLE_SOUND")

        # 6. Audit / Logs
        if re.search(r"\b(?:show audit|audit log|view logs|show logs|intruder log)\b", lower):
            return Command(type="SHOW_AUDIT_LOG")

        # 7. System status
        if re.search(r"\b(?:status|system status|health|system info)\b", lower):
            return Command(type="GET_STATUS")

        # 8. Direct person name query (e.g. "Yadhu" or "Lokesh")
        reserved_words = {"status", "help", "quit", "exit", "logs", "log", "sound", "dip", "flip", "cam", "clear"}
        if lower not in reserved_words and re.match(r"^[a-zA-Z0-9_\s]{2,40}$", clean_text):
            return Command(type="LOCATE_PERSON", target=clean_text)

        # Unknown / unrecognized command
        return Command(type="UNKNOWN_COMMAND", params={"raw": text})

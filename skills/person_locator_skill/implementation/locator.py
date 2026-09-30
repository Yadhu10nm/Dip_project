from typing import List, Optional, Union
from skills.common.types import (
    LocatePersonCommand,
    PersonLocation,
    RecognitionResult,
)


class PersonLocatorSkill:
    """
    Person Locator Skill.
    Active agentic skill that searches real-time recognition results to locate,
    verify, and track a specific requested individual across camera feeds.

    RULES:
    - Rule 9: Only highlights a face whose recognition identity matches the requested person.
    - Rule 10: If no matching face exists, explicitly reports found=False.
    """

    def __init__(self, target_person: Optional[str] = None):
        self.target_person = target_person

    def set_target(self, command_or_name: Union[LocatePersonCommand, str, None]):
        """Sets or clears the current person to locate."""
        if isinstance(command_or_name, LocatePersonCommand):
            self.target_person = command_or_name.person_name.strip()
        elif isinstance(command_or_name, str):
            self.target_person = command_or_name.strip()
        else:
            self.target_person = None

    def clear_target(self):
        """Clears active locate request."""
        self.target_person = None

    def get_target(self) -> Optional[str]:
        return self.target_person

    def locate_in_detections(
        self,
        recognition_results: List[RecognitionResult],
        target_name: Optional[str] = None,
    ) -> PersonLocation:
        """
        Inspects recognition decisions for the current frame to find the target.
        Input:
            recognition_results: List of RecognitionResult objects from the current frame
            target_name: Optional override for the target person
        Output:
            PersonLocation object
        """
        target = (target_name or self.target_person or "").strip().lower()
        if not target:
            return PersonLocation(found=False, name="")

        best_match: Optional[RecognitionResult] = None
        highest_sim = -1.0

        for res in recognition_results:
            if not res.authorized:
                continue

            rec_name = res.name.strip().lower()
            # Match exact name or containment
            if rec_name == target or target in rec_name or rec_name in target:
                if res.similarity > highest_sim:
                    highest_sim = res.similarity
                    best_match = res

        if best_match is not None:
            return PersonLocation(
                found=True,
                name=best_match.name,
                bbox=best_match.bbox,
                similarity=best_match.similarity,
            )

        # Target not visible in current frame
        return PersonLocation(
            found=False,
            name=target_name or self.target_person or "",
            bbox=None,
            similarity=0.0,
        )

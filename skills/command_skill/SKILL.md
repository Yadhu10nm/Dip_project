# Command Skill

## Purpose
Translates natural language text or voice instructions into deterministic, structured `Command` objects for orchestrator execution.

## Responsibilities
- Parse text strings using regular expressions and semantic keyword matching.
- Extract target parameters (such as person names in locate/register requests).
- Standardize command types (`LOCATE_PERSON`, `STOP_LOCATING`, `ENROLL_PERSON`, `TOGGLE_DIP`, `TOGGLE_SOUND`, etc.).
- Forward parsed commands to the central orchestrator or event bus.

## Inputs
- Natural language string (e.g. "locate Yadhu", "enable sound", "stop locating").

## Outputs
- Structured `Command(type: str, target: Optional[str], params: dict)`.

## Tools / Libraries
- Python standard library (`re`).

## Workflow
1. Receive input text string.
2. Clean and normalize whitespace and casing.
3. Match against pattern rules.
4. Extract parameters.
5. Return structured `Command`.

## Commands Understood
- `locate <Name>` / `find <Name>` / `where is <Name>`
- `stop locating` / `clear target`
- `register <Name>` / `enroll <Name>`
- `show DIP mode` / `toggle DIP`
- `enable sound` / `disable sound`
- `show audit log`

## Error Handling
- Returns `None` for empty inputs.
- Emits `type="UNKNOWN_COMMAND"` with original raw text for unparseable strings.

## Performance Requirements
- Sub-millisecond regex parsing.

## Dependencies
- `skills.common.types.Command`

## Example
```python
from skills.command_skill.implementation import CommandSkill

cmd_skill = CommandSkill()
cmd = cmd_skill.parse("find Yadhu")
# Command(type='LOCATE_PERSON', target='Yadhu', params={})
```

## Rules
- **RULE**: The command skill should NOT directly manipulate the camera, database, or hardware.
- It must solely emit structured command objects.

# Text-to-Speech (TTS) Skill

## Purpose
Provides non-blocking, asynchronous acoustic voice announcements for intruder alerts and person locator confirmations using `pyttsx3`.

## Responsibilities
- Maintain a thread-safe message queue.
- Process speech synthesis in a background worker thread.
- Enforce message debounce / cooldown to avoid audio spamming.
- Support runtime mute / unmute toggle.

## Inputs
- Text string to synthesize (e.g. "Warning. Unauthorized person detected.").

## Outputs
- Acoustic audio speech via system speakers.

## Tools / Libraries
- `pyttsx3`
- Python `threading`, `queue`, `time`

## Workflow
1. Skill receives `speak(message)` call.
2. Checks cooldown for the given message text.
3. If valid, pushes text onto FIFO queue.
4. Dedicated worker thread pops text and invokes `pyttsx3.say()` and `runAndWait()`.

## Commands
- `speak(text, force=False)`: Enqueues a voice utterance.
- `set_enabled(bool)`: Controls voice mute state.
- `toggle()`: Inverts active audio state.
- `stop()`: Shuts down background thread.

## Error Handling
- Falls back to logging speech strings to console if audio drivers or sound cards are unavailable.
- Drops messages when queue is full rather than blocking callers.

## Performance Requirements
- `speak()` call completes in under 0.1ms (fire-and-forget).

## Dependencies
- `pyttsx3`

## Example
```python
from skills.tts_skill.implementation import TTSSkill

tts = TTSSkill()
tts.speak("Target Yadhu located on camera one.")
```

## Rules
- **Rule 7**: Do not repeatedly trigger audio for the same event without cooldown.
- **NEVER** block the main vision thread with synchronous speech rendering.

import time
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any


class EventType:
    FRAME_CAPTURED = "FRAME_CAPTURED"
    FACE_DETECTED = "FACE_DETECTED"
    FACE_RECOGNIZED = "FACE_RECOGNIZED"
    UNKNOWN_FACE = "UNKNOWN_FACE"
    AUTHORIZED_PERSON = "AUTHORIZED_PERSON"
    UNAUTHORIZED_PERSON = "UNAUTHORIZED_PERSON"
    LOCATE_REQUESTED = "LOCATE_REQUESTED"
    PERSON_LOCATED = "PERSON_LOCATED"
    PERSON_NOT_FOUND = "PERSON_NOT_FOUND"
    ENROLLMENT_REQUESTED = "ENROLLMENT_REQUESTED"
    ENROLLMENT_COMPLETED = "ENROLLMENT_COMPLETED"
    TTS_REQUESTED = "TTS_REQUESTED"
    EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"
    AUDIT_LOG_ENTRY = "AUDIT_LOG_ENTRY"
    COMMAND_RECEIVED = "COMMAND_RECEIVED"
    DIP_MODE_TOGGLED = "DIP_MODE_TOGGLED"
    SOUND_TOGGLED = "SOUND_TOGGLED"


@dataclass
class Event:
    """Standard event message passed through the EventBus."""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EventBus:
    """
    Thread-safe synchronous/asynchronous Event Bus allowing loose coupling
    between agentic skills.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable[[Event], None]):
        """Register a handler for a given event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]):
        """Unregister a handler."""
        with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)

    def publish(self, event: Event):
        """Dispatch an event to all subscribers synchronously."""
        handlers = []
        with self._lock:
            if event.type in self._subscribers:
                handlers = list(self._subscribers[event.type])
            # Wildcard subscribers
            if "*" in self._subscribers:
                handlers.extend(self._subscribers["*"])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log or print handler error without breaking bus
                print(f"[EventBus] Handler error on {event.type}: {e}")

    def emit(self, event_type: str, **kwargs):
        """Helper to create and dispatch an Event in one call."""
        event = Event(type=event_type, data=kwargs)
        self.publish(event)

from __future__ import annotations

from threading import Event, Lock, Thread
from typing import Callable, Dict

from app.opportunities.models import OpportunityEngineDefinition


class OpportunityScheduler:
    def __init__(self) -> None:
        self._threads: Dict[str, Thread] = {}
        self._stops: Dict[str, Event] = {}
        self._lock = Lock()

    def start(self, definition: OpportunityEngineDefinition, scan: Callable[[], None]) -> bool:
        with self._lock:
            thread = self._threads.get(definition.engine_id)
            if thread and thread.is_alive():
                return False
            stop = Event()
            self._stops[definition.engine_id] = stop

            def loop() -> None:
                while not stop.is_set():
                    scan()
                    stop.wait(max(1, definition.schedule_frequency_minutes) * 60)

            thread = Thread(target=loop, name=f"{definition.engine_id}-scheduler", daemon=True)
            self._threads[definition.engine_id] = thread
            thread.start()
            return True

    def stop(self, engine_id: str) -> None:
        with self._lock:
            stop = self._stops.get(engine_id)
        if stop:
            stop.set()

    def reset_for_tests(self) -> None:
        with self._lock:
            stops = list(self._stops.values())
            self._threads.clear()
            self._stops.clear()
        for stop in stops:
            stop.set()

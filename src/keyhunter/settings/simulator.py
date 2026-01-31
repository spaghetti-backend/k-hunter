import random
from keyhunter.typer.typer import Typer
from keyhunter.content.service import ContentType
from textual import events
from .schemas import AppSettings


class TyperSimulator(Typer):
    def on_settings_change(
        self, old_settings: AppSettings, new_settings: AppSettings
    ) -> None:
        self._simulate_timer.stop()
        super().on_settings_change(old_settings, new_settings)
        self.simulate(pause=False)

    def simulate(self, pause: bool = True):
        self._test_content = self.content_manager.generate(ContentType.SIMPLE, 400)
        self._test_content_idx = 0
        self.engine.prepare_content(self._test_content)
        self._simulate_timer = self.set_interval(0.15, self._simulate_key, pause=pause)
        self.is_active_session = True

    def resume(self):
        self._simulate_timer.resume()

    def pause(self):
        self._simulate_timer.pause()

    def stop(self):
        self._simulate_timer.stop()

    def _simulate_key(self):
        if random.random() < 0.85 and (current_segment := self.engine._current_segment):
            key = current_segment.text
        else:
            key = "a"
        has_next = self.engine.process_key(events.Key(key=key, character=None))
        if not has_next:
            self._simulate_timer.stop()
            self.simulate(pause=False)
        self.refresh()

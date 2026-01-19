from datetime import datetime
from typing import TYPE_CHECKING

from textual import events
from textual.geometry import Size
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from keyhunter.content_manager import ContentManager, ContentType
from keyhunter.settings.schemas import AppSettings, TyperEngine, TyperSettings

from .single_line_engine import SingleLineEngine

if TYPE_CHECKING:
    from datetime import timedelta


class Typer(Widget, can_focus=True):

    class Statistic(Message):
        def __init__(self, elapsed: "timedelta", total: int, correct: int) -> None:
            self.elapsed = elapsed
            self.total = total
            self.correct = correct
            super().__init__()

    def __init__(self, settings: TyperSettings, **kwargs):
        super().__init__(**kwargs)
        self.engine = SingleLineEngine(settings.single_line_engine)
        self.content_manager = ContentManager()
        self.is_active_session: bool = False
        self.styles.border = (
            (settings.border, self.styles.base.color) if settings.border else None
        )
        self.styles.height = (
            settings.single_line_engine.height + 2
            if settings.border
            else settings.single_line_engine.height
        )
        self.styles.width = (
            settings.single_line_engine.width + 2
            if settings.border
            else settings.single_line_engine.width
        )

    def on_mount(self, event: events.Mount) -> None:
        self.watch(self.app, "settings", self.on_settings_change, init=True)
        self.engine.set_chars_style(self.app.available_themes[self.app.theme])
        # self.app.theme_changed_signal.subscribe(self, self.on_theme_change)
        return super()._on_mount(event)

    def on_settings_change(
        self, old_settings: AppSettings, new_settings: AppSettings
    ) -> None:
        if old_settings.theme != new_settings.theme:
            self.on_theme_change(new_settings.theme)
        if old_settings.typer != new_settings.typer:
            if new_settings.typer.typer_engine == TyperEngine.STANDARD:
                raise NotImplementedError("Standard typer engine was not implemented")
            width = new_settings.typer.single_line_engine.width
            self.engine._settings = new_settings.typer.single_line_engine
            self.engine.resize(Size(width, 1))

        self.styles.width = (
            new_settings.typer.single_line_engine.width + 2
            if new_settings.typer.border
            else new_settings.typer.single_line_engine.width
        )

    def on_resize(self, event: events.Resize):
        self.engine.resize(event.container_size)
        self.refresh()

    def on_key(self, event: events.Key) -> None:
        if self.is_active_session:
            if event.key == "escape":
                self.stop_typing()
            else:
                has_next = self.engine.process_key(event)

                if not has_next:
                    self.stop_typing()
        elif event.key == "space":
            self.engine.prepare_content(
                self.content_manager.generate(ContentType.WORDS, 10)
            )
            self.start_typing()
        else:
            return None

        event.stop()
        self.refresh()

    def on_theme_change(self, theme: str) -> None:
        self.engine.set_chars_style(self.app.available_themes[theme])

    def start_typing(self) -> None:
        self.is_active_session = True
        self._start_time = datetime.now()

    def stop_typing(self) -> None:
        self.post_message(
            self.Statistic(
                datetime.now() - self._start_time,
                self.engine.total_chars,
                self.engine.correct_chars,
            )
        )

        self.is_active_session = False

    def retry(self) -> None:
        pass

    def render_line(self, y: int) -> Strip:
        # if y >= self.container_size.height:
        #     return Strip.blank(self.container_size.width)

        if not self.is_active_session:
            return self.engine.build_placeholder(y, self.content_manager.placeholder)

        return self.engine.build_line(y)

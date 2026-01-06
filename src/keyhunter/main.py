from datetime import datetime
from typing import TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.app import App, ComposeResult
from textual.containers import CenterMiddle
from textual.message import Message
from textual.strip import Strip
from textual.theme import Theme
from textual.widget import Widget
from textual.widgets import Static


if TYPE_CHECKING:
    from datetime import timedelta


class OneLineTyper:
    success_style = Style.parse("green")
    wrong_style = Style.parse("red")
    default_style = Style.parse("white")
    next_style = default_style + Style(underline=True)
    _width = 0

    def __init__(self) -> None:
        self._segments = []
        self._type_results = []
        self._current_segment_idx = 0
        self._before_center = 0
        self._after_center = 0

    @property
    def _current_segment(self) -> Segment:
        return self._segments[self._current_segment_idx]

    @_current_segment.setter
    def _current_segment(self, current_segment: Segment) -> None:
        self._segments[self._current_segment_idx] = current_segment

    @property
    def total_chars(self):
        return len(self._segments) - self._before_center - self._after_center

    @property
    def correct_chars(self):
        return sum(self._type_results)

    def _update_current_segment(self, style: Style) -> None:
        self._current_segment = Segment(self._current_segment.text, style)

    def _update_segments(self, type_result: bool) -> bool:
        if type_result:
            self._update_current_segment(self.success_style)
        else:
            self._update_current_segment(self.wrong_style)

        self._current_segment_idx += 1

        if self._current_segment_idx < (len(self._segments) - self._after_center):
            self._update_current_segment(self.next_style)
            return True
        else:
            return False

    def set_chars_style(self, theme: Theme) -> None:
        def segment_style(self, style: Style | None) -> Style:
            match style:
                case self.success_style:
                    return success_style
                case self.wrong_style:
                    return wrong_style
                case self.next_style:
                    return next_style
                case _:
                    return default_style

        bgcolor = theme.background if theme.background else "#111111"
        default_style = Style(color=theme.foreground, bgcolor=bgcolor)
        success_style = Style(color=theme.success, bgcolor=bgcolor)
        wrong_style = Style(color=theme.error, bgcolor=bgcolor)
        next_style = default_style + Style(underline=True)

        self._segments = [
            Segment(
                text=segment.text,
                style=segment_style(self, segment.style),
            )
            for segment in self._segments
        ]

        self.default_style = default_style
        self.success_style = success_style
        self.wrong_style = wrong_style
        self.next_style = next_style

    def set_text(self, text: str) -> None:
        text = " ".join(text.split())
        self._type_results.clear()

        before_segments = [
            Segment(" ", self.default_style) for _ in range(self._before_center)
        ]
        after_segments = [
            Segment(" ", self.default_style) for _ in range(self._after_center)
        ]

        self._segments = (
            before_segments
            + [Segment(char, self.default_style) for char in text]
            + after_segments
        )

        self._current_segment_idx = self._before_center
        self._update_current_segment(self.next_style)

    def resize(self, width: int) -> None:
        self._width = width
        before_center, addition = divmod(width, 2)
        after_center = before_center + addition

        if self._segments:
            before_segments = [
                Segment(" ", self.default_style) for _ in range(before_center)
            ]
            after_segments = [
                Segment(" ", self.default_style) for _ in range(after_center)
            ]

            self._segments = (
                before_segments
                + self._segments[
                    self._before_center : (len(self._segments) - self._after_center)
                ]
                + after_segments
            )

        self._current_segment_idx = (
            self._current_segment_idx - self._before_center + before_center
        )
        self._before_center = before_center
        self._after_center = after_center

    def process_key(self, key: events.Key) -> bool:
        type_result = self._current_segment.text == key.character
        self._type_results.append(type_result)

        return self._update_segments(type_result)

    def make_initial_strip(self, _: int, text: str) -> Strip:
        text = f"{text:^{self._width}}"

        return Strip([Segment(char, self.default_style) for char in text])

    def make_typing_strip(self, _: int) -> Strip:
        if not self._segments:
            return Strip.blank(self._width)

        start = max(0, self._current_segment_idx - self._before_center)
        end = min(
            self._current_segment_idx + self._after_center, (len(self._segments) - 1)
        )

        return Strip(self._segments[start:end])


class Typer(Widget, can_focus=True):
    TEXT = """The ScrollView class requires a virtual size, which is the size of the scrollable content and should be set via the virtual_size property. If this is larger than the widget then Textual will add scrollbars.
    We need to update the render_line method to generate strips for the visible area of the widget, taking into account the current position of the scrollbars.

    Let's add scrolling to our checkerboard example. A standard 8 x 8 board isn't sufficient to demonstrate scrolling so we will make the size of the board configurable and set it to 100 x 100, for a total of 10,000 squares."""

    class Statistic(Message):
        def __init__(self, elapsed: "timedelta", total: int, correct: int) -> None:
            self.elapsed = elapsed
            self.total = total
            self.correct = correct
            super().__init__()

    def __init__(self):
        super().__init__()
        self.typer = OneLineTyper()
        self.is_typing = False
        self.styles.height = 1

    def on_mount(self, event: events.Mount) -> None:
        self.typer.set_chars_style(self.app.available_themes[self.app.theme])
        self.app.theme_changed_signal.subscribe(self, self.on_theme_change)
        return super()._on_mount(event)

    def on_resize(self, event: events.Resize):
        self.typer.resize(event.container_size.width)
        self.refresh()

    def on_key(self, event: events.Key) -> None:
        if not self.is_typing:
            if event.key == "space":
                event.stop()
                self.typer.set_text(self.TEXT)
                self.start_typing()
                self.refresh()

            return None

        event.stop()

        has_next = self.typer.process_key(event)

        if not has_next:
            self.stop_typing()

        self.refresh()

    def on_theme_change(self, theme: Theme) -> None:
        self.typer.set_chars_style(theme)

    def start_typing(self) -> None:
        self.is_typing = True
        self._start_time = datetime.now()

    def stop_typing(self) -> None:
        self.post_message(
            self.Statistic(
                datetime.now() - self._start_time,
                self.typer.total_chars,
                self.typer.correct_chars,
            )
        )

        self.is_typing = False

    def render_line(self, y: int) -> Strip:
        if y >= self.container_size.height:
            return Strip.blank(self.container_size.width)

        if not self.is_typing:
            return self.typer.make_initial_strip(y, "Press 'space' to start typing")

        return self.typer.make_typing_strip(y)


class KeyHunter(App):

    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield CenterMiddle(Typer())
        yield Static("Statistic")

    def on_typer_statistic(self, message: Typer.Statistic) -> None:
        statistic = self.query_one(Static)

        statistic.update(
            f"{message.correct}/{message.total}({round(message.correct/message.total*100, 2)}) for {message.elapsed}, avg={round(message.total/(message.elapsed.seconds/60), 2)}"
        )


def main():
    app = KeyHunter()
    app.run()
    # app.run(inline=True)


if __name__ == "__main__":
    main()

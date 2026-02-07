from textual.app import ComposeResult
from textual.containers import CenterMiddle, HorizontalGroup
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from .schemas import TypingSessionSummary


class StatisticRow(HorizontalGroup):
    def __init__(
        self, label: str, data: str, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.label = label
        self.data = data

    def compose(self) -> ComposeResult:
        yield Label(content=self.label, classes="statistic-label")
        yield Label(content=self.data, classes="statistic-data")


class TypingSummaryView(Widget):
    typing_summary: reactive[TypingSessionSummary | None] = reactive(
        None, recompose=True
    )

    def __init__(
        self, typing_summary: TypingSessionSummary | None = None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.set_reactive(TypingSummaryView.typing_summary, typing_summary)

    def compose(self) -> ComposeResult:
        if not self.typing_summary:
            yield Label("Your typing statistics will be shown here")
        else:
            yield StatisticRow(
                label="Accuracy",
                data=self.typing_summary.accuracy,
                classes="statistic-row",
            )

            yield StatisticRow(
                label="Elapsed time",
                data=self.typing_summary.time,
                classes="statistic-row",
            )

            yield StatisticRow(
                label="Speed", data=self.typing_summary.speed, classes="statistic-row"
            )


class Profile(CenterMiddle):
    def compose(self) -> ComposeResult:
        yield TypingSummaryView(id="stat")

    async def update_last_typing_result(
        self, typing_summary: TypingSessionSummary
    ) -> None:
        self.query_one(TypingSummaryView).typing_summary = typing_summary

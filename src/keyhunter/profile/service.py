from datetime import datetime, timedelta
from typing import Sequence

from keyhunter.typer.schemas import Keystroke

from .schemas import TypingSessionSummary, TypingSummary
from .storage import SQLite3Storage

MILLISECONDS_MULTIPLIER = 1000
PERCENT_SCALE_2DP = 10_000
FLOAT_TO_INT_SCALE_2DP = 100


class ProfileService:

    def __init__(self) -> None:
        self._storage = SQLite3Storage()
        self._last_session_summary = self._load_last_session_summary()
        self._today_summary = self._load_sessions_summary(today_only=True)
        self._all_time_summary = self._load_sessions_summary(today_only=False)

    @property
    def last_session(self) -> TypingSessionSummary:
        return self._last_session_summary

    @property
    def today(self) -> TypingSummary:
        return self._today_summary

    @property
    def all_time(self) -> TypingSummary:
        return self._all_time_summary

    def _load_last_session_summary(self) -> TypingSessionSummary:
        try:
            speed, accuracy, elapsed_time_ms = self._storage.load_last_session_summary()
            return TypingSessionSummary(
                speed=self._as_cpm(speed),
                accuracy=self._as_percent(accuracy),
                time=self._convert_time(elapsed_time_ms),
            )
        except TypeError:
            return TypingSessionSummary()

    def _load_sessions_summary(self, today_only: bool) -> TypingSummary:
        try:
            (
                sessions_count,
                speed_avg,
                speed_max,
                accuracy_avg,
                accuracy_max,
                sessions_time_ms,
            ) = self._storage.load_sessions_summary(today_only=today_only)

            return TypingSummary(
                time=self._convert_time(sessions_time_ms),
                typing_sessions=str(sessions_count),
                speed_avg=self._as_cpm(speed_avg),
                speed_max=self._as_cpm(speed_max),
                accuracy_avg=self._as_percent(accuracy_avg),
                accuracy_max=self._as_percent(accuracy_max),
            )
        except TypeError:
            return TypingSummary()

    def add(self, typing_summary: Sequence[Keystroke]) -> TypingSessionSummary:
        keystrokes = sorted(typing_summary, key=lambda x: x.key)
        keystrokes_summary = []
        session_summary = {
            "total_chars": 0,
            "correct_chars": 0,
            "elapsed_time_ms": 0,
        }

        last_char = keystrokes[0].key
        char_summary = {
            "char": last_char,
            "total": 0,
            "correct": 0,
            "elapsed_time_ms": 0,
        }

        for keystroke in keystrokes:
            if keystroke.key != last_char:
                keystrokes_summary.append(char_summary)
                last_char = keystroke.key
                char_summary = {
                    "char": last_char,
                    "total": 0,
                    "correct": 0,
                    "elapsed_time_ms": 0,
                }

            char_summary["total"] += 1
            char_summary["correct"] += keystroke.is_matched
            char_summary["elapsed_time_ms"] += keystroke.elapsed_time_ms

        for summary in keystrokes_summary:
            total_chars = summary["total"]
            correct_chars = summary["correct"]
            elapsed_time_ms = summary["elapsed_time_ms"]

            summary["accuracy"] = self._compute_typing_accuracy(
                total_chars, correct_chars
            )
            summary["speed"] = self._compute_typing_speed(total_chars, elapsed_time_ms)

            session_summary["total_chars"] += total_chars
            session_summary["correct_chars"] += correct_chars
            session_summary["elapsed_time_ms"] += elapsed_time_ms

        session_total_chars = session_summary["total_chars"]
        session_correct_chars = session_summary["correct_chars"]
        session_elapsed_time_ms = session_summary["elapsed_time_ms"]
        session_accuracy = self._compute_typing_accuracy(
            total_chars=session_total_chars,
            correct_chars=session_correct_chars,
        )
        session_speed = self._compute_typing_speed(
            total_chars=session_summary["total_chars"],
            elapsed_time_ms=session_summary["elapsed_time_ms"],
        )

        session_summary["accuracy"] = session_accuracy
        session_summary["speed"] = session_speed

        self._storage.add_session_summary(session_summary, keystrokes_summary)

        self._last_session_summary = TypingSessionSummary(
            speed=self._as_cpm(session_speed),
            accuracy=self._as_percent(session_accuracy),
            time=self._convert_time(session_elapsed_time_ms),
        )

        self._today_summary = self._load_sessions_summary(today_only=True)
        self._all_time_summary = self._load_sessions_summary(today_only=False)

        return self._last_session_summary

    def _convert_time(self, elapsed_time_ms: int) -> str:
        dt = datetime.min
        delta = timedelta(milliseconds=elapsed_time_ms)
        format = "%d days %H:%M:%S" if delta.days else "%H:%M:%S"
        return (dt + delta).strftime(format)

    def _as_cpm(self, speed: int) -> str:
        return f"{speed / FLOAT_TO_INT_SCALE_2DP}cpm"

    def _as_percent(self, accuracy: int) -> str:
        return f"{accuracy / FLOAT_TO_INT_SCALE_2DP}%"

    def _compute_typing_accuracy(self, total_chars: int, correct_chars: int) -> int:
        accuracy = round((correct_chars / total_chars) * PERCENT_SCALE_2DP)
        return int(accuracy)

    def _compute_typing_speed(self, total_chars: int, elapsed_time_ms: int) -> int:
        minutes = elapsed_time_ms / (60 * MILLISECONDS_MULTIPLIER)
        cpm = round((total_chars / minutes) * 100)
        return int(cpm)

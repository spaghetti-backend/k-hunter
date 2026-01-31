import random
from enum import Enum, auto
from typing import Final

DATASETS: Final = "src/keyhunter/content/datasets/"


class ContentType(Enum):
    SIMPLE = auto()
    WORDS = auto()


class ContentService:
    def __init__(self) -> None:
        self._seek = 0

    def generate(self, text_type: ContentType, length: int, offset: int = 0) -> str:
        match text_type:
            case ContentType.SIMPLE:
                filepath = f"{DATASETS}en/simple.txt"
                with open(filepath) as f:
                    f.seek(offset)
                    return f.read(length)
            case ContentType.WORDS:
                filepath = f"{DATASETS}en/common_1000.txt"
                with open(filepath) as f:
                    data = [f.readline() for _ in range(length)]
                random.shuffle(data)
                return "\n".join(data)

    @property
    def placeholder(self) -> str:
        return "Press 'space' to start typing"

import random
from enum import Enum, auto


class ContentType(Enum):
    SIMPLE = auto()
    WORDS = auto()


class ContentManager:
    def __init__(self) -> None:
        self._seek = 0

    def generate(self, text_type: ContentType, length: int, offset: int = 0) -> str:
        match text_type:
            case ContentType.SIMPLE:
                with open("src/keyhunter/datasets/en/simple.txt") as f:
                    f.seek(offset)
                    return f.read(length)
            case ContentType.WORDS:
                with open("src/keyhunter/datasets/en/common_1000.txt") as f:
                    data = [f.readline() for _ in range(length)]
                random.shuffle(data)
                return "\n".join(data)

    @property
    def placeholder(self) -> str:
        return "Press 'space' to start typing"

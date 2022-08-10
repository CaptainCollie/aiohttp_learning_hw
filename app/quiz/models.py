from dataclasses import dataclass
from typing import Optional


@dataclass
class Theme:
    id: Optional[int]
    title: str


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Question:
    id: Optional[int]
    theme_id: int
    title: str
    answers: list[Answer]

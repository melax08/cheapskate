from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self


@dataclass
class BaseSerializer(ABC):
    @abstractmethod
    def get_message(self) -> str:
        raise NotImplementedError

    def get_labeled_message(self, label: str) -> str:
        return f"{label}\n\n{self.get_message()}"

    @classmethod
    @abstractmethod
    def from_api_response(cls, response_data: dict) -> Self:
        raise NotImplementedError

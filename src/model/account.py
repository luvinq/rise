from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Account:
    id: int
    private_key: str
    proxy: Optional[str]

    def __str__(self) -> str:
        return f"Account {self.id}"

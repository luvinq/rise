import random
from abc import ABC

from src import config


class Service(ABC):

    @property
    def _random_delay(self) -> int:
        return random.randint(0, config.DELAY_MAX * 60)

    @property
    def _random_amount(self) -> float:
        return round(random.uniform(config.AMOUNT_MIN, config.AMOUNT_MAX), 12)

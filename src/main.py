import asyncio
import random
from typing import List

from src import config
from src.model import Account
from src.service import *


def load_accounts() -> List[Account]:
    with open("accounts.json", "r", encoding="utf-8") as file:
        import json
        accounts = json.load(file)

    return [Account(id=index + 1, **account) for index, account in enumerate(accounts)]


async def main():
    # Accounts
    accounts = load_accounts()
    semaphores = {account: asyncio.Semaphore(1) for account in accounts}

    # Services
    native = Native()
    gas_pump = GasPump()
    inari = Inari()

    # Tasks
    tasks = []
    for account in accounts:
        semaphore = semaphores[account]

        available_tasks = [
            lambda: native.send_eth(semaphore, account),
            lambda: gas_pump.wrap_eth(semaphore, account),
            lambda: gas_pump.unwrap_eth(semaphore, account),
            lambda: inari.supply(semaphore, account),
        ]

        actual_tasks = [
            task() for task in available_tasks
            for _ in range(random.randint(1, config.RUN_TIMES_MAX))
        ]

        tasks.extend(actual_tasks)

    # Waiting for all tasks to end
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

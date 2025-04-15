import asyncio
import random
from asyncio import Semaphore
from typing import Tuple, Optional

from loguru import logger
from web3 import AsyncWeb3

from src import utils
from src.model import Account
from src.service import Service

INARI_ADDRESS = "0x81edb206Fd1FB9dC517B61793AaA0325c8d11A23"
INARI_ABI = [
    {
        "type": "function",
        "name": "supply",
        "inputs": [
            {
                "name": "asset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "onBehalfOf",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "referralCode",
                "type": "uint16",
                "internalType": "uint16"
            }
        ],
    },
]

ERC20_ABI = [
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ]
    },
    {
        "type": "function",
        "name": "approve",
        "inputs": [
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ]
    },
]


class Inari(Service):

    def __init__(self):
        self._tokens = [
            # symbol, address, spender
            ("WBTC", "0xF32D39ff9f6Aa7a7A64d7a4F00a54826Ef791a55", "0x81edb206Fd1FB9dC517B61793AaA0325c8d11A23"),
            ("USDC", "0x8A93d247134d91e0de6f96547cB0204e5BE8e5D8", "0x81edb206Fd1FB9dC517B61793AaA0325c8d11A23"),
            ("USDT", "0x40918ba7f132e0acba2ce4de4c4baf9bd2d7d849", "0x81edb206Fd1FB9dC517B61793AaA0325c8d11A23"),
            ("WETH", "0x4200000000000000000000000000000000000006", "0x81edb206Fd1FB9dC517B61793AaA0325c8d11A23"),
        ]

    async def supply(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > Inari > Supply"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as w3:
            address = w3.eth.account.from_key(account.private_key).address

            # Getting random token with positive balance
            result = await self._get_random_token_with_balance(w3, address)
            if result is None:
                logger.bind(tag=tag).warning("There are no tokens with positive balance")
                return

            token, amount_wei = result  # unpacking

            # Approving token if needed
            await self._approve_token_if_needed(w3, account, token, amount_wei, tag)

            # Supplying token
            amount = w3.from_wei(amount_wei, "ether")
            logger.bind(tag=tag).info(f"Supplying {amount:.12f} {token[0]}")

            contract = w3.eth.contract(
                address=w3.to_checksum_address(INARI_ADDRESS),
                abi=INARI_ABI
            )

            tx = await contract.functions.supply(
                token[1],  # asset
                amount_wei,  # amount
                address,  # onBehalfOf
                0,  # referralCode
            ).build_transaction({
                "from": address,
            })

            await utils.perform_transaction(w3, tx, account.private_key, tag)

    async def _get_random_token_with_balance(self, w3: AsyncWeb3, address: str) -> Optional[Tuple[Tuple[str, str, str], int]]:
        random.shuffle(self._tokens)
        for token in self._tokens:
            contract = w3.eth.contract(
                address=w3.to_checksum_address(token[1]),
                abi=ERC20_ABI
            )

            balance = await contract.functions.balanceOf(
                address,  # owner
            ).call()
            if balance > 0:
                # Using 20-40% of balance
                amount_wei = int(balance * random.uniform(0.2, 0.4))
                return token, amount_wei

            # Sleeping 1 second before next check
            await asyncio.sleep(1)

        return None

    async def _approve_token_if_needed(self, w3: AsyncWeb3, account: Account, token: Tuple[str, str, str], amount_wei: int, tag: str):
        contract = w3.eth.contract(
            address=w3.to_checksum_address(token[1]),
            abi=ERC20_ABI
        )

        address = w3.eth.account.from_key(account.private_key).address
        spender = w3.to_checksum_address(token[2])
        allowance_wei = await contract.functions.allowance(
            address,  # owner
            spender,  # spender
        ).call()

        if amount_wei <= allowance_wei:
            return

        logger.bind(tag=tag).info(f"Approving {token[0]}")

        approval = await contract.functions.approve(
            spender,  # spender
            2 ** 256 - 1,  # amount
        ).build_transaction({
            "from": address,
        })

        await utils.perform_transaction(w3, approval, account.private_key, tag)

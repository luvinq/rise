import random
from asyncio import Semaphore

from loguru import logger
from web3 import AsyncWeb3

from src import utils
from src.model import Account
from src.service import Service

WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
WETH_ABI = [
    {
        "type": "function",
        "name": "deposit",
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "withdraw",
        "inputs": [
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
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
                "name": "amount",
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
    }
]


class GasPump(Service):

    async def wrap_eth(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > Wrap ETH"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as w3:
            amount = self._random_amount
            logger.bind(tag=tag).info(f"Wrapping {amount:.12f} ETH")

            contract = w3.eth.contract(
                address=w3.to_checksum_address(WETH_ADDRESS),
                abi=WETH_ABI
            )

            tx = await contract.functions.deposit().build_transaction({
                "value": w3.to_wei(amount, 'ether'),
            })

            await utils.perform_transaction(w3, tx, account.private_key, tag)

    async def unwrap_eth(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > Unwrap ETH"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as w3:
            contract = w3.eth.contract(
                address=w3.to_checksum_address(WETH_ADDRESS),
                abi=WETH_ABI
            )

            address = w3.eth.account.from_key(account.private_key).address
            balance_wei = await contract.functions.balanceOf(address).call()
            if balance_wei == 0:
                logger.bind(tag=tag).warning(f"No WETH balance")
                return

            # Using 20-40% of balance
            amount_wei = int(balance_wei * random.uniform(0.2, 0.4))
            await self._approve_weth_if_needed(w3, account, amount_wei, tag)

            amount = w3.from_wei(amount_wei, 'ether')
            logger.bind(tag=tag).info(f"Unwrapping {amount:.12f} ETH")

            tx = await contract.functions.withdraw(
                amount_wei,  # amount
            ).build_transaction({
                "from": address,
            })

            await utils.perform_transaction(w3, tx, account.private_key, tag)

    async def _approve_weth_if_needed(self, w3: AsyncWeb3, account: Account, amount_wei: int, tag: str):
        contract = w3.eth.contract(
            address=w3.to_checksum_address(WETH_ADDRESS),
            abi=WETH_ABI
        )

        address = w3.eth.account.from_key(account.private_key).address
        spender = w3.to_checksum_address("0x143bE32C854E4Ddce45aD48dAe3343821556D0c3")
        allowance_wei = await contract.functions.allowance(
            address,  # owner
            spender,  # spender
        ).call()

        if amount_wei <= allowance_wei:
            return

        logger.bind(tag=tag).info(f"Approving WETH")

        approval = await contract.functions.approve(
            spender,  # spender
            2 ** 256 - 1,  # amount
        ).build_transaction({
            "from": address,
        })

        await utils.perform_transaction(w3, approval, account.private_key, tag)

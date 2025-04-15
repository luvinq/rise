from asyncio import Semaphore

from loguru import logger

from src import utils
from src.model import Account, RiseChain
from src.service import Service


class Native(Service):

    async def send_eth(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > Send ETH"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as web3:
            amount = self._random_amount
            logger.bind(tag=tag).info(f"Sending {amount:.12f} ETH to myself")

            address = web3.eth.account.from_key(account.private_key).address

            tx = {
                'chainId': RiseChain.chain_id,
                'from': address,
                'to': address,
                'value': web3.to_wei(amount, 'ether'),
            }

            await utils.perform_transaction(web3, tx, account.private_key, tag)

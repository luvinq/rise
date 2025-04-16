import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from loguru import logger
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth

from src.model import RiseChain


#
# Common
#

async def delay(delay_: float, tag: str):
    if delay_ <= 0:
        return

    hours = delay_ // 3600
    remaining = delay_ % 3600
    minutes = remaining // 60
    seconds = remaining % 60

    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not time_parts:
        time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    time_str = " ".join(time_parts)
    logger.bind(tag=tag).info(f"Sleeping {time_str}")
    await asyncio.sleep(delay_)


#
# Web3
#

@asynccontextmanager
async def web3_session(semaphore: asyncio.Semaphore, proxy: Optional[str], tag: str):
    await semaphore.acquire()

    rpc = RiseChain.rpc
    web3 = AsyncWeb3(
        AsyncHTTPProvider(
            endpoint_uri=rpc,
            request_kwargs={'proxy': proxy},
        ),
        modules={'eth': AsyncEth},
    )

    try:
        proxy_str = f"via proxy: {proxy}" if proxy else "without proxy"
        logger.bind(tag=tag).info(f"Connecting to {rpc} {proxy_str}")
        if not await web3.is_connected():
            logger.bind(tag=tag).error(f"Connection failed")
            raise ConnectionError

        yield web3
    except Exception as e:
        logger.bind(tag=tag).error(e)
    finally:
        await web3.provider.disconnect()
        await asyncio.sleep(10)
        semaphore.release()


async def perform_transaction(w3: AsyncWeb3, transaction, private_key: str, tag: str):
    address = w3.eth.account.from_key(private_key).address

    transaction["gas"] = await w3.eth.estimate_gas(transaction)
    gas_price = await w3.eth.gas_price
    transaction["maxFeePerGas"] = gas_price
    transaction["maxPriorityFeePerGas"] = gas_price

    transaction["nonce"] = await w3.eth.get_transaction_count(address)
    transaction["type"] = 2

    value = transaction.get("value", 0)
    transaction_cost = value + transaction["gas"]

    balance = await w3.eth.get_balance(address)
    if balance < transaction_cost:
        balance_ether = w3.from_wei(balance, "ether")
        transaction_cost_ether = w3.from_wei(transaction_cost, "ether")
        logger.bind(tag=tag).critical(f"Low balance: {balance_ether:.12f} ETH. Tx cost: {transaction_cost_ether:.12f} ETH")
        return

    logger.bind(tag=tag).info("Performing transaction")

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)
    tx_hash_hex = w3.to_hex(tx_hash)

    message = f"View on explorer > {RiseChain.explorer}/tx/{tx_hash_hex}"
    if tx_receipt["status"] == 1:
        logger.bind(tag=tag).success(message)
    else:
        logger.bind(tag=tag).error(message)

    return tx_receipt

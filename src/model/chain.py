from dataclasses import dataclass


@dataclass(frozen=True)
class Chain:
    name: str
    rpc: str
    chain_id: int
    symbol: str
    explorer: str


RiseChain = Chain(
    name="Rise Testnet",
    rpc="https://testnet.riselabs.xyz",
    chain_id=11155931,
    symbol="ETH",
    explorer="https://explorer.testnet.riselabs.xyz"
)

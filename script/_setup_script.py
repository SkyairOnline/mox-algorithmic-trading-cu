from boa.contracts.abi.abi_contract import ABIContract
from typing import Tuple
from moccasin.config import get_active_network
import boa

STARTING_ETH_BALANCE = int(1000e18)
STARTING_WETH_BALANCE = int(1e18)
STARTING_USDC_BALANCE = int(100e6)

def _add_eth_balance():
    boa.env.set_balance(boa.env.eoa, STARTING_ETH_BALANCE)

def _add_token_balance(usdc, weth):
    weth.deposit(value=STARTING_WETH_BALANCE)
    our_address = boa.env.eoa
    with boa.env.prank(usdc.owner()):
        usdc.updateMasterMinter(our_address)
    usdc.configureMinter(our_address, STARTING_USDC_BALANCE)
    usdc.mint(our_address, STARTING_USDC_BALANCE)

def setup_script() -> Tuple[ABIContract, ABIContract, ABIContract, ABIContract]:
    active_network = get_active_network()

    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")

    if active_network.is_local_or_forked_network():
        _add_eth_balance()
        _add_token_balance(usdc, weth)
    
    aave_protocol_data_provider = active_network.manifest_named("aave_protocol_data_provider")
    a_tokens = aave_protocol_data_provider.getAllATokens()

    a_usdc = None
    a_weth = None

    token_prefix = ""
    if active_network.chain_id == 324:  # ZkSync Era
        token_prefix = "aZks"
    if active_network.chain_id == 1:
        token_prefix = "aEth"
    else:
        token_prefix = ""
    
    for a_token in a_tokens:
        if f"{token_prefix}USDC" in a_token[0]:
            a_usdc = active_network.manifest_named("usdc", address=a_token[1])
        if f"{token_prefix}WETH" in a_token[0]:
            a_weth = active_network.manifest_named("usdc", address=a_token[1])

    print(f"USDC balance: {usdc.balanceOf(boa.env.eoa)}")  
    print(f"WETH balance: {weth.balanceOf(boa.env.eoa)}")  
    print(f"aUSDC balance: {a_usdc.balanceOf(boa.env.eoa)}")  # Raw USDC balance
    print(f"aWETH balance: {a_weth.balanceOf(boa.env.eoa)}")  # Raw WETH balance
    return usdc, weth, a_usdc, a_weth
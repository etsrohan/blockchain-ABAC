from web3 import Web3
from web3 import middleware
from web3.middleware import geth_poa_middleware

ACCOUNTS = (
    "0xbB66eF34814f0613a3B738288FE55553A69C44BA",
    "0x6a09436F3Cb7C3e871071033ABA967327499b9d4",
    "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a",
    "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B",
    "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23",
    "0xa72e420605FD940b860c493263ce891d434782CB",
    "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D",
    "0xe1ac1b434331F1c57b909947eC20393819Ad462f",
    "0xD9c258d8aA168add0E5183C9725c1C7C0712868A",
    "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90",
    "0x877f503365C0b55F4259208D4327daF6BDC66d01",
    "0x59e8e60540c5204402Ee39490381c206B77fc7eE",
    "0xD5956cfB4Bb948ADcE1033580b85257C624c29d7",
    "0x0cE5C86d596cB1446f561503c33721Ca43236603"
)


INFURA_URL = "https://goerli.infura.io/v3/60febbc1f74c4e229c6f6f694ea571ac"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if w3.isConnected:
    print('[CONNECTED] Goerli Ethereum Test Network Connection Established!')
    print(w3.eth.blockNumber)
    
w3.middleware_onion.inject(geth_poa_middleware, layer = 0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

for address in ACCOUNTS:
    print(f'Balance for Address 0x...{address[-4:]}: {w3.eth.get_balance(address)}')
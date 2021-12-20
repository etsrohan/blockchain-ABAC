from web3 import Web3
from web3 import middleware
from web3.middleware import geth_poa_middleware

ACCOUNTS = {
    "0xbB66eF34814f0613a3B738288FE55553A69C44BA": "bee41af6acfa1c6f430646b8744e2f435f251db087971f38e5d9f2ea3a0b79c4",
    "0x6a09436F3Cb7C3e871071033ABA967327499b9d4": "890d4a07e4f4aa790111fe8b2a5d07c84de8a708d51c48487416b892b905c010",
    "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a": "a2a0d0097c87754d45cff13ecb81f697b30106db553250eea411da48ca5bef4a",
    "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B": "ef741d30314c0cfa147f2c0f409349c587a5a27b4003b8e5cdf0490e6eaa588d",
    "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23": "64778725d0104b96b58dad5d21bce443b806bf322b4d58d82afc60b279532a0c",
    "0xa72e420605FD940b860c493263ce891d434782CB": "a18a2c18ed46edb5b6c4fe2a52a69373c7929b34489ac9b193cc313ff2a01c7d",
    "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D": "91b403bd0ced9eff20eb3c8bf388bdc5641fa33978770ac8487ca7406950cb0d",
    "0xe1ac1b434331F1c57b909947eC20393819Ad462f": "d1b539ffd7dd1624370b09025ec2f6d649e9c8e7c55077370d696e181effe83a",
    "0xD9c258d8aA168add0E5183C9725c1C7C0712868A": "b4d3426cd39722b35050289379616ff6d0dd4e8c6256881a4601daf826d2bab8",
    "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90": "b637439846fab4659ee39e98ab8655f5e2f5ca719c25fb9004426fe9d0a361dd",
    "0x877f503365C0b55F4259208D4327daF6BDC66d01": "876545b242014e371ab56e55f5553d5efda45b73df4280c7bc13754224fead9a",
    "0x59e8e60540c5204402Ee39490381c206B77fc7eE": "74c0d94ea62b05a396c066ec6bf5fb64ca4c31b8b993f5a1383e9278318e13fe",
    "0xD5956cfB4Bb948ADcE1033580b85257C624c29d7": "8feaed78e867d6aebd5bab7c5f835b25a0f17b7f191316d16650e63d9bd16ecf",
    "0x0cE5C86d596cB1446f561503c33721Ca43236603": "09892cc8797addb00fd5b0c69802e0ee4ae3f776a63b63a82a86c7ebf083c3e9"
}


INFURA_URL = "https://goerli.infura.io/v3/60febbc1f74c4e229c6f6f694ea571ac"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer = 0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

if w3.isConnected():
    print('[CONNECTED] Goerli Ethereum Test Network Connection Established!')
    print(w3.eth.blockNumber)

for address in ACCOUNTS:
    print(f'Balance for Address 0x...{address[-4:]}: {w3.eth.get_balance(address)}')
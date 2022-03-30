import logging
import os
import random
import yaml
from logging import config
from web3 import Web3
from web3.middleware import geth_poa_middleware, construct_sign_and_send_raw_middleware, time_based_cache_middleware, latest_block_based_cache_middleware, simple_cache_middleware

from web3.gas_strategies.time_based import fast_gas_price_strategy

def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOGGING_CONFIG_FILE'):
    """
    :param default_path: 
    :param default_level: 
    :param env_key: 
    :return: 
    """
    log_path = default_path
    log_value = os.getenv(env_key, None)
    if log_value:
        log_path = log_value
    if os.path.exists(log_path):
        with open(log_path) as fh:
            config.dictConfig(yaml.safe_load(fh.read()))
        logging.getLogger(__name__).info("Logging configured with config file!")
    else:
        logging.basicConfig(format='%(asctime)-15s %(levelname)-4s %(threadName)s %(message)s',
                        level=(default_level))
        logging.getLogger(__name__).info("Logging configured with default attributes!")
    # Suppress requests and web3 verbose logs
    logging.getLogger("requests").setLevel(logging.INFO)
    logging.getLogger("web3").setLevel(logging.INFO)

def setup_web3(args):
    w3 = Web3(Web3.HTTPProvider(args.rpc_url))
    
    # Middleware to sign transactions from a private key
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(args.eth_key))
    w3.eth.default_account = w3.eth.account.from_key(args.eth_key).address
    
    # Gas Middleware
    w3.eth.set_gas_price_strategy(fast_gas_price_strategy)

    # Caching middleware
    w3.middleware_onion.add(time_based_cache_middleware)
    w3.middleware_onion.add(latest_block_based_cache_middleware)
    w3.middleware_onion.add(simple_cache_middleware)

    return w3

def add_randomness(price: float, lower: float, upper: float)->float:
    return round(price + random.uniform(lower, upper), 2)


def randomize_default_price(price: float)->float:
    return add_randomness(price, -0.1, 0.1)

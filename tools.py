""" Useful function, tools and constants across moduls """

import time
from datetime import datetime
from json.decoder import JSONDecodeError
import logging
import requests


# logger used in modules
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="logging.log",
    encoding="utf-8",
    level=logging.INFO,
)
logger.addHandler(console_handler)


# Constants used in modules
now_dt = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
now_ts = int((time.time()))
yesterday = now_ts - (24 * 60 * 60)
black_list = {
    "0x0000000000000000000000000000000000000000",
    "0xdEAD000000000000000042069420694206942069",
}
BLOCK_NUM = "https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={api_key}"

GET_WALLETS = "https://api.etherscan.io/api?module=account&action=tokentx&page=1&offset=10000&sort=asc&contractaddress={token}&apikey={api_key}&startblock={sblock}&endblock={eblock}"

ETH_TX = "https://api.etherscan.io/api?module=account&action=txlist&address={wallet}page=1&offset=10000&sort=asc&startblock={sblock}&endblock=99999999&&apikey={api_key}"

TOKEN_TX = "https://api.etherscan.io/api?module=account&action=tokentx&address={wallet}&page=1&offset=10000&sort=asc&startblock={sblock}&endblock=99999999&apikey={api_key}"


def get_block_number(api_key: str, **kwargs):
    """Get block_number by date_time or timestamp.
    GIVE DATE_TIME AS STRING,
    WITH THIS FORMAT: date_time=%Y/%m/%d %H:%M:%S
    OR timestamp=int"""

    if "date_time" in kwargs:
        d_t = datetime.strptime(kwargs["date_time"], "%Y/%m/%d %H:%M:%S")
        timestamp = int(datetime.timestamp(d_t))
    else:
        timestamp = kwargs["timestamp"]

    url = BLOCK_NUM.format(timestamp=timestamp, api_key=api_key)

    block_num = try_request(url)
    if block_num["flag"]:
        logger.critical("Connection/request error returning -1 for block_num")
        return -1

    block_num = try_json(block_num["response"])
    if block_num["flag"]:
        logger.critical("Json error returning -1 for block_num")
        return -1

    return block_num["data"]["result"]


### End of get_block_number


def try_req_json(url) -> dict:
    """Get response and make it json"""

    res = try_request(url)
    if res["flag"]:
        return {}

    res = try_json(res["response"])
    if res["flag"]:
        return {}

    return res["data"]


### End of try_req_json


def try_request(url) -> dict:
    """Exception handling and retrying requests"""

    flag = response = False
    for err_count in range(1, 6):

        try:
            response = requests.get(url, timeout=20)
            time.sleep(0.25)
            break

        except requests.exceptions.RequestException:
            logger.critical("Connection/request error, trying %i", err_count)
            time.sleep(0.25)
            if err_count == 5:
                flag = True
            continue
    # End of exception handling loop

    return {"flag": flag, "response": response}


### End of try_request


def try_json(response) -> dict:
    """Exception handling .json()"""

    flag = data = False
    try:
        data = response.json()
        test = data["message"]
        test += "just testing"

    except (JSONDecodeError, KeyError, TypeError):
        logger.critical("Json error...")
        flag = True

    return {"flag": flag, "data": data}


### End of try_json

"""This module contains functions to extract and track ETH wallets.

Functions:
    get_wallets: Gets information needed to extract wallets.
    grade_wallets: Labels wallets which were repeated.
    track_wallets: Gets the true token tx for each wallet and compare.
Local import:
    import tools

Functions are based on working with files mostly. So you need to have
The directories related to each function in the same directory with
this module.
Examples:
    wallets.get_wallets(
        token: "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
        api_key: "A_VALID_ETH_SCAN_API_KEY",
        start: "2022/05/21 13:50:30",
        end: "2022/05/22 13:50:30"
        filename: "shiba_may_22"
        is_buy: True
    )
    With the above example the function will extract all wallets
    which had at least one transaction on the specified token
    and in that transaction the wallet got the token, not vice versa.
    Meaning that the wallet bought the token and the "to" key in the
    transaction is equal to the wallet itself.
    For more information, see:
    https://docs.etherscan.io/api-endpoints/accounts
    *#get-a-list-of-erc20-token-transfer-events-by-address*
"""

import os
import sys

import tools


# ---------------------------------------------------------------------
def get_wallets(
    token: str, api_key: str, start: str, end: str, filename: str, is_buy: bool
) -> None:
    """Gets information needed to extract wallets.

    Args:
        token (str): The token to extract wallets from.
        api_key (str): The API key to authenticate with.
        start (str): The start date of the transactions.
        end (str): The end date of the transactions.
        filename (str): The name of the file to save the final result.
        is_buy (bool): Whether check for buys or sells.
    Returns:
        None
    """

    tools.logger.info("%s Starting get_wallets %s", "=" * 30, "=" * 30)
    tools.logger.info("Token: %s file_name: %s", token, filename)

    path = f'wallets/{"buy" if is_buy else "sell"}_{filename}.txt'

    if os.path.isfile(path):
        check = (input(f"{path} already exists. Overwrite? y/n: ")).lower()
        if check == "n":
            print("Please backup first and run the program again")
            sys.exit()

    with open(path, mode="w", encoding="utf-8", newline="\n"):
        pass

    sblock = tools.get_block_number(api_key=api_key, date_time=start)
    eblock = tools.get_block_number(api_key=api_key, date_time=end)

    while True:
        tools.logger.info("Getting wallets sblock: %s", sblock)

        url = tools.GET_WALLETS.format(
            token=token, api_key=api_key, sblock=sblock, eblock=eblock
        )

        res = tools.try_req_json(url)
        if not res:
            tools.logger.critical("Closing due to req/json error...")
            break

        tools.logger.info("res length: %i", len(res["result"]))

        wallets = {tx["to"] if is_buy else tx["from"] for tx in res["result"]}

        with open(path, mode="r+", encoding="utf-8", newline="\n") as f:
            dup_check = f.read()
            for wallet in wallets:
                if wallet not in dup_check and wallet not in tools.black_list:
                    f.writelines([wallet + "\n"])

        if len(res["result"]) < 10000:
            tools.logger.info("Token: %s file_name: %s", token, filename)
            tools.logger.info("%s End of get_wallets %s", "=" * 30, "=" * 30)
            break
        sblock = res["result"][-1]["blockNumber"]
    # End of while loop


# ---------------------------------------------------------------------
def grade_wallets(result_filename: str) -> None:
    """Labels wallets which were repeated.

    Args:
        result_filename (str): The filename for saving results.
    Returns:
        None
    """

    tools.logger.info("%s Starting grade_wallets %s", "=" * 30, "=" * 30)
    tools.logger.info("file_name: %s", result_filename)

    if len(os.listdir("wallets")) < 2:
        tools.logger.info("Only one file. Nothing to be done.")
        return None

    files = {}
    for file in os.listdir("wallets"):
        with open(f"wallets/{file}", encoding="utf-8") as f:
            files[file.replace(".txt", "")] = f.read().split()

    tools.logger.info("files: %s", str(files.values()))

    all_wallets = [wallet for wallets in files.values() for wallet in wallets]
    duplicates = {
        wallet for wallet in all_wallets if all_wallets.count(wallet) > 1
    }
    tools.logger.info(
        "All: %i Duplicates: %i", len(all_wallets), len(duplicates)
    )

    final_result = {}
    for wallet in duplicates:
        for file_name, wallets in files.items():
            if wallet in wallets:
                if not final_result.get(wallet):
                    final_result[wallet] = file_name + ","
                else:
                    final_result[wallet] += file_name + ","

    path = f"graded/{result_filename}.txt"
    with open(path, mode="a", encoding="utf-8", newline="\n") as f:
        for wallet, description in final_result.items():
            f.writelines([wallet + "," + description + "\n"])

    print("Current wallets directory: ", os.listdir("wallets"))
    check = input("You're actually done with them. Delete all? y/n").lower()
    if check == "y":
        for file in os.listdir("wallets"):
            os.remove(file)

    tools.logger.info("file_name: %s", result_filename)
    tools.logger.info("%s End grade_wallets %s", "=" * 30, "=" * 30)

    return None


# ---------------------------------------------------------------------
def track_wallets(api_key: str) -> None:
    """Gets the true token tx for each wallet and compare.
    Args:
        api_key (str): The API key to use for authentication.
    Returns:
        None
    """

    yesterday = tools.get_block_number(
        api_key=api_key, timestamp=tools.yesterday
    )

    # Read the file containing wallets + description
    wallets = {}
    with open(
        "tracking/tracking.txt", mode="r", encoding="utf-8", newline="\n"
    ) as f:

        lines = f.readlines()
        for line in lines:
            line = line.split(",")
            if (line[0]) not in tools.black_list:
                wallets[line[0]] = ",".join(line[1:])

    final_result = {}
    for wallet, description in wallets:

        result = _get_results(wallet=wallet, sblock=yesterday, api_key=api_key)
        if not result:
            continue

        eth_hash = {tx["hash"] for tx in result["eth"]}
        # Having these hashes helps to prevent collecting token contracts
        # which wasn't bought actually, and they're just send or receive.

        tokens = {
            tx["contractAddress"]
            for tx in result["token"]
            if tx["hash"] in eth_hash
        }

        # If there's a tx for a token, which it's not in eth_hashes,
        # It's just a simple send or receive.
        # And it can be easily done by anyone.
        # Specially by scam token owners!!!
        # So, it's better to prevent saving those from the beginning.

        for token in tokens:
            if final_result.get(token):
                final_result[token] += "BUYER" + description
            else:
                final_result[token] = "BUYER" + description
    # End of loop (wallets)

    path = f"tracking_results/result_{str(tools.now_dt)}.txt"
    with open(path, mode="w", encoding="utf-8", newline="\n") as f:

        for token, buyers in final_result.items():
            if buyers.count("BUYER") > 5:
                f.writelines([token + "," + buyers + "\n"])


# ---------------------------------------------------------------------
def _get_results(wallet: str, sblock: int, api_key: str) -> dict:
    token = tools.TOKEN_TX.format(
        wallet=wallet, sblock=sblock, api_key=api_key
    )

    eth = tools.ETH_TX.format(wallet=wallet, sblock=sblock, api_key=api_key)

    token = tools.try_req_json(token)
    eth = tools.try_req_json(eth)

    if not token or not eth:
        tools.logger.critical("Skipping wallet %s", wallet)
        return {}

    return {"token": token["result"], "eth": eth["result"]}

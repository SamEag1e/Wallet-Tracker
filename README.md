# Wallet-Tracker
## Description
A tool for extracting and tracking Smart Ethereum (ETH) wallets. Future updates will extend functionality to support Binance Smart Chain (BSC) and TON blockchains.

## Features
- **Extract Wallets**: Retrieve information needed to extract wallets.
- **Grade Wallets**: Label wallets which were repeated.
- **Track Wallets**: Get the true token transactions for each wallet and compare.
- **Future Support**: Planned support for Binance Smart Chain (BSC) and TON blockchains.

## Installation
* Clone the repository:
```bash
git clone https://github.com/SamEag1e/Wallet-Tracker.git
```
* Navigate to the project directory:
```
cd Wallet-Tracker
```
* Open the main.py with a code editor and follow the [Example Usage](#Example-Usage)  steps.
## Example Usage
```
Python

wallets.get_wallets(
    token="0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
    api_key="A_VALID_ETH_SCAN_API_KEY",
    start="2022/05/21 13:50:30",
    end="2022/05/22 13:50:30",
    filename="shiba_may_22",
    is_buy=True
)
```
With the above example, the function will extract all wallets which had
at least one transaction on the specified token and in that transaction,
the wallet got the token, not vice versa. Meaning that the wallet bought
the token and the “to” key in the transaction is equal to the wallet itself.

## Contributing
* Fork the repository.
* Create a new branch (git checkout -b feature-branch).
* Commit your changes (git commit -m 'Add new feature').
* Push to the branch (git push origin feature-branch).
* Open a pull request.
## Contact
For any inquiries, please contact me at:

* **Email**: samadeagle@yahoo.com
* **Telegram**: SamadTnd
## License
This project is licensed under the MIT License.

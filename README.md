# ⚡ Rise Testnet Script

![](https://blog.risechain.com/content/images/size/w2000/2025/04/Frame-2147223945.png)

## ⭐ Features

- **Transfers:** Send ETH to yourself
- **Gas Pump:** Wrap/Unwrap ETH, token approvals
- **Inari:** Supply random tokens, token approvals
- **...**


- **Multi-account Support:** Use many accounts with proxies
- **Easy Setup:** Add, remove, and view accounts through a user-friendly CLI

## 📦 Installation

1. Clone the repository

```shell
git clone https://github.com/luvinq/rise.git
cd rise
```

2. Install dependencies

```shell
pip install -r requirements.txt
```

## 📝 Configuration

1. Configure your accounts

```shell
python accounts.py
```

2. (Optional) Configure script settings in `src/config.py`

```python
AMOUNT_MIN = 0.000001     # Minimal amount for one action
AMOUNT_MAX = 0.00001      # Maximal amount for one action

DELAY_MAX = 30            # Maximal delay for one action (in minutes!)

RUN_TIMES_MAX = 3         # Maximal action run times
```

## ❓ What the script does

- For `each account`
- The script will run `every action`
- Random times from `1` to `RUN_TIMES_MAX`
- With random delay from `0` to `DELAY_MAX`
- Using from `AMOUNT_MIN` to `AMOUNT_MAX` tokens

## 🚀 Usage

⚠️ Before running the script make sure your accounts have positive ETH
balance

```shell
python -m src.main
```

ETH and other tokens are available at https://portal.risechain.com/

## 😢 Problems

If you have any problems, contact me via https://t.me/iamluvin
and I will try to help you ❤️

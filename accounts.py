import json
import os

CONFIG_FILE = 'accounts.json'


def load_accounts():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_accounts(accounts):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)


def list_accounts(accounts):
    if not accounts:
        print("\nNo accounts\n")
        return
    print("\nAccounts:")
    for i, acc in enumerate(accounts):
        print(f"{i + 1}. Private Key: {acc['private_key']} | Proxy: {acc.get('proxy', 'None')}")
    print()


def add_account(accounts):
    print("\nAdd a new account:")
    private_key = input("Enter private key: ").strip()
    if not private_key:
        print("❌ Private key is required\n")
        return

    proxy = input("Enter proxy in format http://login:password@ip:port (enter to skip): ").strip()
    account = {
        "private_key": private_key,
        "proxy": None
    }
    if proxy:
        account["proxy"] = proxy

    accounts.append(account)
    save_accounts(accounts)
    print("\n✅ Account added\n")


def remove_account(accounts):
    if not accounts:
        print("\nThere are no accounts to remove\n")
        return

    try:
        index = int(input("\nEnter the number of the account to remove: ")) - 1
        if 0 <= index < len(accounts):
            accounts.pop(index)
            save_accounts(accounts)
            print(f"\n✅ Account removed\n")
        else:
            print("\n❌ Invalid number")
    except ValueError:
        print("❌ Please enter a valid number\n")


def main_menu():
    while True:
        accounts = load_accounts()
        list_accounts(accounts)

        print("Options:")
        print("1. Add account")
        print("2. Remove account")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == '1':
            add_account(accounts)
        elif choice == '2':
            remove_account(accounts)
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice. Please enter a number from 1 to 3\n")


if __name__ == '__main__':
    main_menu()

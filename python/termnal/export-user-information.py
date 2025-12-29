import requests
import json
import os
import argparse

def get_token(cli_token=None):
    if cli_token:
        return cli_token

    env_token = os.getenv("NOBITEX_TOKEN")
    if env_token:
        return env_token

    token = input("Enter your Nobitex token: ")

    if not token:
        print("Token is required!")
        return None
    return token

def fetch_profile(base_url, headers):
    profile_url = f"{base_url}/users/profile"
    try:
        resp = requests.get(profile_url, headers=headers)
        resp.raise_for_status()
        return resp.json().get("profile", {})
    except requests.exceptions.RequestException as e:
        print("Failed to fetch profile:", e)
        return {}

def fetch_wallets_list(base_url, headers):
    url = f"{base_url}/users/wallets/list"
    try:
        resp = requests.post(url, headers=headers)
        resp.raise_for_status()
        return resp.json().get("wallets", [])
    except requests.exceptions.RequestException as e:
        print("Failed to fetch wallets list:", e)
        return []

def extract_balances(wallets):
    irt_balance = 0.0
    usdt_balance = 0.0

    for wallet in wallets:
        currency = wallet.get("currency", "").upper()
        available = float(wallet.get("activeBalance", 0))
        if currency in ["IRT", "RLS", "IRR"]:
            irt_balance += available
        if currency == "USDT":
            usdt_balance += available

    return irt_balance, usdt_balance

def main():
    base_url = "https://apiv2.nobitex.ir"
    parser = argparse.ArgumentParser(description="Export Nobitex user information")
    parser.add_argument("--token", help="Nobitex API token")
    args = parser.parse_args()

    token = get_token(args.token)
    if not token:
        print("Token not provided. Exiting.")
        return

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
        "User-Agent": "PythonClient/1.0"
    }

    profile = fetch_profile(base_url, headers)
    if not profile:
        print("Could not fetch profile. Check your token and connection.")
        return

    wallets = fetch_wallets_list(base_url, headers)
    irt_balance, usdt_balance = extract_balances(wallets)

    result = {
        "name": profile.get("firstName", ""),
        "last_name": profile.get("lastName", ""),
        "phone_number": profile.get("mobile", ""),
        "email": profile.get("email", ""),
        "irt_balance": irt_balance,
        "usdt_balance": usdt_balance
    }

    filename = f"{token}-{profile.get('email','user')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("User info:")
    print(json.dumps(result, indent=4))
    print(f"Data exported to {filename}")

if __name__ == "__main__":
    main()

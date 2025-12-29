import requests
import json
import os
import argparse
import time

def get_token(cli_token=None):
	if cli_token:
		return cli_token

	env_token = os.getenv("NOBITEX_TOKEN")
	if env_token:
		return env_token

	token = input("Enter your Nobitex token: ")
	if not token:
		print("codent find token")
		return None
	return token


def get_wallets(headers, base_url):
    try:
        resp = requests.post(f"{base_url}/users/wallets/list", headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("wallets", [])
    except requests.exceptions.RequestException:
        return None


def main():
	base_url = "https://apiv2.nobitex.ir"
	parser = argparse.ArgumentParser(description="Sell 1 USDT on Nobitex (market)")
	parser.add_argument("--token", help="Nobitex API token")
	args = parser.parse_args()

	token = get_token(args.token)
	if not token:
		return

	headers = {
		"Authorization": f"Token {token}",
		"Content-Type": "application/json",
		"User-Agent": "PythonClient/1.0"
	}

	# check balances first
	wallets = get_wallets(headers, base_url)
	if wallets is None:
		print("Could not fetch wallets")
		return

	usdt_balance = 0.0
	for w in wallets:
		cur = w.get("currency", "").upper()
		if cur == "USDT":
			try:
				usdt_balance += float(w.get("activeBalance", 0))
			except Exception:
				pass

	if usdt_balance <= 0:
		print("no balance")
		return

	payload = {
		"type": "sell",
		"srcCurrency": "usdt",
		"dstCurrency": "rls",
		"amount": "1",
		"execution": "market",
		"clientOrderId": f"sell-1-usdt-{int(time.time())}"
	}

	try:
		resp = requests.post(f"{base_url}/market/orders/add", headers=headers, json=payload, timeout=15)
	except requests.exceptions.RequestException as e:
		print("Failed to place sell order:", e)
		return

	# Try to parse JSON response and handle API-level errors
	try:
		data = resp.json()
	except ValueError:
		print(f"Unexpected non-JSON response (status {resp.status_code}):")
		print(resp.text)
		return

	# API may return HTTP 200 but status "failed" in body
	if resp.status_code != 200 or data.get("status") == "failed":
		print("Order failed:")
		print(json.dumps(data, indent=4, ensure_ascii=False))
		return

	# success
	print("selled succesfully")
	print(json.dumps(data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
	main()
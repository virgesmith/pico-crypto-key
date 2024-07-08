from datetime import datetime, timezone

from pico_crypto_key.device import CryptoKey

import requests

HOST = "http://localhost:8000"
USER = "user1"

def main() -> None:
    with CryptoKey() as key:
        version, timestamp = key.info()
        print(f"{version} @ {timestamp}")
        while True:
            try:
                match cmd := input("\nRegister/Auth/Quit? (r/a/q) "):
                    case "r":
                        pubkey = key.register(HOST).hex()
                        print(f"Registering {USER} with {HOST}: pubkey is {pubkey}")
                        response = requests.get(f"{HOST}/register", params={"username": USER, "pubkeyhex": pubkey})
                        response.raise_for_status()
                        print(response.json())
                    case "a":
                        _, timestamp = key.info()
                        now = datetime.now(tz=timezone.utc)
                        print(f"Host-device time diff: {(now - timestamp).total_seconds()}s")

                        response = requests.get(f"{HOST}/challenge")
                        response.raise_for_status()
                        challenge = response.json()
                        token = key.auth(HOST, challenge.encode()).decode()
                        print(f"Authenticating {USER} with {HOST} using challenge='{challenge}'")
                        print(f"Token: {token}")
                        response = requests.get(f"{HOST}/login", params={"username": USER}, headers={"token": token})
                        response.raise_for_status()
                        print(response.json())
                    case "q":
                        break
                    case _:
                        print(f"Invalid input: {cmd}")
            except requests.exceptions.HTTPError as e:
                print(e)


if __name__ == "__main__":
    main()

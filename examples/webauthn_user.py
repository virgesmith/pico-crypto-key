from datetime import datetime, timezone

import requests

from pico_crypto_key.device import CryptoKey, CryptoKeyNotFoundError

HOST = "http://localhost:8000"


def main() -> None:
    try:
        with CryptoKey() as key:
            version, timestamp = key.info()
            print(f"{version} @ {timestamp}")
            print(f"Interacting with {HOST}")
            while True:
                _, timestamp = key.info()
                now = datetime.now(tz=timezone.utc)
                print(f"Host-device time diff: {(now - timestamp).total_seconds()}s")
                try:
                    match cmd := input("\nRegister/Auth/List/Quit? (r/a/q) "):
                        case "r":
                            user = input("username: ")
                            username = f"{user}@{HOST}"

                            # first request challenge
                            response = requests.get(f"{HOST}/challenge", params={"username": user})
                            response.raise_for_status()
                            challenge = response.json()

                            # retrieve pubkey
                            pubkey = key.register(username).hex()
                            # generate token
                            token = key.auth(username, challenge.encode()).decode()

                            print(f"Registering {user}@{HOST}: pubkey is {pubkey}")
                            response = requests.get(f"{HOST}/register", params={"username": user, "pubkeyhex": pubkey}, headers={"token": token})
                            response.raise_for_status()
                            print(response.json())
                        case "a":
                            user = input("username: ")
                            username = f"{user}@{HOST}"

                            response = requests.get(f"{HOST}/challenge", params={"username": user})
                            response.raise_for_status()
                            challenge = response.json()
                            token = key.auth(username, challenge.encode()).decode()
                            print(f"Authenticating {username} using challenge='{challenge}' at {now}")
                            print(f"Token: {token}")
                            response = requests.get(
                                f"{HOST}/login", params={"username": user}, headers={"token": token}
                            )
                            response.raise_for_status()
                            print(response.json())
                        case "q":
                            break
                        case _:
                            print(f"Invalid input: {cmd}")
                except requests.exceptions.HTTPError as e:
                    print(e)
    except CryptoKeyNotFoundError:
        print("Key not found, is it connected?")


if __name__ == "__main__":
    main()

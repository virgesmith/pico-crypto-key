from datetime import datetime, timezone

import requests

from pico_crypto_key.device import CryptoKey, CryptoKeyNotFoundError


def get_challenge(host: str, user: str) -> str:
    response = requests.get(f"{host}/challenge", params={"username": user})
    response.raise_for_status()
    return response.json()


def main() -> None:
    HOST = "http://localhost:8000"
    try:
        with CryptoKey() as key:
            version, timestamp = key.info()
            print(f"{version} @ {timestamp}")
            print(f"Interacting with {HOST}")
            while True:
                _, timestamp = key.info()
                now = datetime.now(tz=timezone.utc)
                print(f"Device time diff: {(now - timestamp).total_seconds()}s")
                try:
                    match cmd := input("\nRegister/Auth/List/Quit? (r/a/q) "):
                        case "r":
                            user = input("username: ")
                            challenge = get_challenge(HOST, user)

                            # retrieve pubkey
                            pubkey = key.register(HOST, user).hex()
                            # generate token
                            token = key.auth(HOST, user, challenge.encode()).decode()

                            print(f"Registering {user}@{HOST}: pubkey is {pubkey}")
                            response = requests.get(
                                f"{HOST}/register",
                                params={"username": user, "pubkeyhex": pubkey},
                                headers={"token": token},
                            )
                            response.raise_for_status()
                            print(response.json())
                        case "a":
                            user = input("username: ")

                            challenge = get_challenge(HOST, user)

                            token = key.auth(HOST, user, challenge.encode()).decode()

                            print(f"Authenticating {user}@{HOST} using challenge='{challenge}' at {now}")
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

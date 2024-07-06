from datetime import datetime, timezone

from pico_crypto_key.device import CryptoKey

hosts = ["example.com", "othersite.net"]


def select_host() -> int:
    print("Available hosts:")
    for i, h in enumerate(hosts):
        print(f"{i+1:>2d}. {h}")
    while True:
        raw = input()
        if raw.isdigit() and 0 < int(raw) < len(hosts) + 1:
            return hosts[int(raw) - 1]


def main() -> None:
    global hosts
    with CryptoKey() as key:
        version, timestamp = key.info()
        print(f"{version} @ {timestamp}")
        while True:
            match cmd := input("\nRegister/Auth/Quit? (r/a/q) "):
                case "r":
                    host = input("Host: ")
                    pubkey = key.register(host)
                    print(f"Registering with {host}: pubkey is {pubkey.hex()}")
                    hosts.append(host)
                case "a":
                    _, timestamp = key.info()
                    now = datetime.now(tz=timezone.utc)
                    print(f"Host-device time diff: {(now - timestamp).total_seconds()}s")

                    host = select_host()

                    challenge = input("Challenge string: ")
                    token = key.auth(host, challenge.encode()).decode()
                    print(f"Authenticating with {host} using challenge={challenge}")
                    print(f"Token: {token}")
                case "q":
                    break
                case _:
                    print(f"Invalid input: {cmd}")


if __name__ == "__main__":
    main()

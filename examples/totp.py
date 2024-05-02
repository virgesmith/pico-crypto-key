"""
Example: change the device pin.
"""

from datetime import datetime, timezone

from pico_crypto_key import CryptoKey


def totp() -> None:
    with CryptoKey() as crypto_key:
        timestamp_ms = crypto_key.totp()
        utc = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        print(utc)


if __name__ == "__main__":
    totp()

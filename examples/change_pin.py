"""
Example: change the device pin.
"""

from pico_crypto_key import CryptoKey, CryptoKeyNotFoundError


def change_pin() -> None:
    try:
        with CryptoKey() as crypto_key:
            crypto_key.set_pin()
    except CryptoKeyNotFoundError:
        print("Key not connected")


if __name__ == "__main__":
    change_pin()

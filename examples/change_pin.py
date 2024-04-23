"""
Example: change the device pin.
"""

from pico_crypto_key import CryptoKey

def change_pin() -> None:
    with CryptoKey() as crypto_key:
        result = crypto_key.set_pin()
    print(result)


if __name__ == "__main__":
    change_pin()

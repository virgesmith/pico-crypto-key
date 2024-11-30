"""
Example: change the device pin.
"""

from pico_crypto_key import CryptoKey, CryptoKeyConnectionError, CryptoKeyPinError


def change_pin() -> None:
    try:
        with CryptoKey() as crypto_key:
            crypto_key.set_pin()
    except CryptoKeyConnectionError:
        print("Key not connected")
    except CryptoKeyPinError:
        print("PIN incorrect")


if __name__ == "__main__":
    change_pin()

"""
Example 0: compute SHA256 hash of a file.
"""

import toml

from pico_crypto_key import CryptoKey

if __name__ == "__main__":
    config = toml.load("./pyproject.toml")["pico"]["run"]

    with CryptoKey(pin=config["PICO_CRYPTO_KEY_PIN"]) as crypto_key:
        hash = crypto_key.hash(__file__)
    print(f"{__file__}: {hash.hex()}")

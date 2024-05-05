"""
Example: compute SHA256 hash of a file.
"""

from pico_crypto_key import CryptoKey, CryptoKeyNotFoundError


def hash_file(file: str) -> None:
    try:
        with CryptoKey() as crypto_key:
            digest = crypto_key.hash(file)
        print(f"{__file__}: {digest.hex()}")
    except CryptoKeyNotFoundError:
        print("Key not connected")


if __name__ == "__main__":
    hash_file(__file__)

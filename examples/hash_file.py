"""
Example: compute SHA256 hash of a file.
"""

from pico_crypto_key import CryptoKey

def hash_file(file: str) -> None:
    with CryptoKey() as crypto_key:
        digest = crypto_key.hash(file)
    print(f"{__file__}: {digest.hex()}")


if __name__ == "__main__":
    hash_file(__file__)

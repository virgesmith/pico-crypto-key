"""
Example: compute SHA256 hash of a file.
"""

import sys
from pathlib import Path

from pico_crypto_key import CryptoKey, CryptoKeyNotFoundError, CryptoKeyPinError


def hash_file(file: Path) -> None:
    try:
        with CryptoKey() as crypto_key:
            version, _ = crypto_key.info()
            print(f"PicoCryptoKey {version}")
            digest = crypto_key.hash(file)
        print(f"{file}: {digest.hex()}")
    except CryptoKeyNotFoundError:
        print("Key not connected")
    except CryptoKeyPinError:
        print("PIN incorrect")


if __name__ == "__main__":
    assert len(sys.argv) == 2
    filename = Path(sys.argv[1])
    assert filename.is_file()
    hash_file(filename)

"""
Example: use a second (or original) device to verify an ECDSA signature.
"""

import json
from pathlib import Path
from time import time

from pico_crypto_key import CryptoKey, CryptoKeyConnectionError, CryptoKeyPinError


def verify_data(signature_file: Path) -> None:
    try:
        if not signature_file.is_file():
            print(f"{signature_file} not found (need to run sign_data.py first)")
        with CryptoKey() as crypto_key, open(signature_file) as fd:
            version, _ = crypto_key.info()
            print(f"PicoCryptoKey {version}")
            signature = json.load(fd)
            # first check hash matches file
            start = time()
            digest = crypto_key.hash(signature["file"])
            if digest != bytes.fromhex(signature["hash"]):
                print("file hash doesn't match signature hash")
                return
            else:
                print("file hash matches file")

            sig = bytes.fromhex(signature["signature"])
            pubkey = bytes.fromhex(signature["pubkey"])
            if crypto_key.pubkey() == pubkey:
                print("verifying device is the signing device")
            else:
                print("verifying device is not the signing device")

            if crypto_key.verify(digest, sig, pubkey):
                print("signature is not valid")
            else:
                print("signature is valid")
            print(f"verifying took {time() - start:.2f}s")
    except CryptoKeyConnectionError:
        print("Key not connected")
    except CryptoKeyPinError:
        print("PIN incorrect")


if __name__ == "__main__":
    verify_data(Path("signature.json"))

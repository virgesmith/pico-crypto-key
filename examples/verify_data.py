"""
Example 3: 
Use a second (or original) device to verify a data signature of given a public key (as hex strings).
"""

import json
import os
from time import time

import toml

from pico_crypto_key import CryptoKey


def verify_data(signature_file: str, device_pin: str) -> None:
    if not os.stat(signature_file):
        print(f"{signature_file} not found (need to run sign_data.py first)")
    with CryptoKey(pin=device_pin) as crypto_key:
        with open(signature_file) as fd:
            signature = json.load(fd)
            # first check hash matches file
            start = time()
            hash = crypto_key.hash(signature["file"])
            if hash != bytes.fromhex(signature["hash"]):
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

            if crypto_key.verify(hash, sig, pubkey):
                print("signature is not valid")
            else:
                print("signature is valid")
            print(f"verifying took {time()-start:.2f}s")


if __name__ == "__main__":
    config = toml.load("./pyproject.toml")["pico"]["run"]

    verify_data("signature.json", config["PICO_CRYPTO_KEY_PIN"])

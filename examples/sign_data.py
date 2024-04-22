"""
Example 2: Use device to sign a dataset, returning (in json format) the hash, 
signature and public key (as hex strings) for verification.
"""

import json
import time

import toml

from pico_crypto_key import CryptoKey


def sign_data(filename: str, device_pin: str) -> None:
    with CryptoKey(pin=device_pin) as device:
        start = time.time()
        pubkey = device.pubkey()
        digest, signature = device.sign(filename)
        print("signing/verifying took %.2fs" % (time.time() - start))

        result = dict(
            file=filename,
            hash=digest.hex(),
            signature=signature.hex(),
            pubkey=pubkey.hex(),
        )
        with open("signature.json", "w") as fd:
            json.dump(result, fd, indent=2)
        print("signature written to signature.json")


if __name__ == "__main__":
    filename = "./examples/dataframe.csv"
    config = toml.load("./pyproject.toml")["pico"]["run"]

    sign_data(filename, config["PICO_CRYPTO_KEY_PIN"])

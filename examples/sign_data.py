"""
Example: Use device to sign a dataset, returning (in json format) the hash,
signature and public key (as hex strings) for verification.
"""

import json
import time

from pico_crypto_key import CryptoKey


def sign_data(filename: str) -> None:
    with CryptoKey() as device:
        start = time.time()
        pubkey = device.pubkey()
        digest, signature = device.sign(filename)
        print("signing took %.2fs" % (time.time() - start))

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
    sign_data(filename)

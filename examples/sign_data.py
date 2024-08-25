"""
Example: Use device to sign a dataset, returning (in json format) the hash,
signature and public key (as hex strings) for verification.
"""

import json
import time
from pathlib import Path

from pico_crypto_key import CryptoKey, CryptoKeyNotFoundError, CryptoKeyPinError


def sign_data(filename: Path) -> None:
    try:
        with CryptoKey() as device:
            version, _ = device.info()
            print(f"PicoCryptoKey {version}")
            start = time.time()
            pubkey = device.pubkey()
            digest, signature = device.sign(filename)
            print("signing took %.2fs" % (time.time() - start))

            result = dict(
                file=str(filename),
                hash=digest.hex(),
                signature=signature.hex(),
                pubkey=pubkey.hex(),
            )
            with open("signature.json", "w") as fd:
                json.dump(result, fd, indent=2)
            print("signature written to signature.json")
    except CryptoKeyNotFoundError:
        print("Key not connected")
    except CryptoKeyPinError:
        print("PIN incorrect")


if __name__ == "__main__":
    filename = Path("./examples/dataframe.csv")
    sign_data(filename)

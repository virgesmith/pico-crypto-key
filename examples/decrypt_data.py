"""
Example: use device to encrypt a dataset (if not already present) and read an encrypted dataset into a pandas dataframe.
"""

from io import BytesIO
from pathlib import Path
from time import time

import pandas as pd  # type: ignore

from pico_crypto_key import CryptoKey, CryptoKeyConnectionError, CryptoKeyPinError


def read_encrypted_dataframe(ciphertext: Path) -> None:
    try:
        with CryptoKey() as crypto_key:
            version, _ = crypto_key.info()
            print(f"PicoCryptoKey {version}")
            ciphertext = filename
            # if the encrypted data isn't there, create it from the plaintext
            if not ciphertext.is_file():
                print("Generating ciphertext")
                plaintext = ciphertext.with_suffix("")
                print(plaintext)
                start = time()
                with open(plaintext, "rb") as p, open(ciphertext, "wb") as c:
                    c.write(crypto_key.encrypt(p.read()))
                print("encryption took %.2fs" % (time() - start))

            # now decrypt in-memory
            start = time()
            with open(ciphertext, "rb") as c:
                df = pd.read_csv(BytesIO(crypto_key.decrypt(c.read())))
            print("decryption took %.2fs" % (time() - start))
            print(df)
    except CryptoKeyConnectionError:
        print("Key not connected")
    except CryptoKeyPinError:
        print("PIN incorrect")


if __name__ == "__main__":
    filename = Path("examples/dataframe.csv.enc")
    read_encrypted_dataframe(filename)

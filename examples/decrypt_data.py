"""
Example: use device to encrypt a dataset (if not already present) and read an encrypted dataset into a pandas dataframe.
"""

import os
from io import BytesIO
from time import time

import pandas as pd  # type: ignore

from pico_crypto_key import CryptoKey, CryptoKeyNotFoundError


def read_encrypted_dataframe(ciphertext: str) -> None:
    try:
        with CryptoKey() as crypto_key:
            ciphertext = filename
            # if the encrypted data isn't there, create it from the plaintext
            if not os.path.isfile(ciphertext):
                print("Generating ciphertext")
                plaintext = ciphertext.replace(".enc", "")
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
    except CryptoKeyNotFoundError:
        print("Key not connected")


if __name__ == "__main__":
    filename = "examples/dataframe.csv.enc"
    read_encrypted_dataframe(filename)

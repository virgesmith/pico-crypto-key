"""
Example 1: use device to read an encrypted dataset into a pandas dataframe.
"""

import os
from io import BytesIO
from time import time

import pandas as pd  # type: ignore
import toml

from pico_crypto_key import CryptoKey


def read_encrypted_dataframe(ciphertext: str, device_pin: str) -> None:
    with CryptoKey(pin=device_pin) as crypto_key:
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


if __name__ == "__main__":
    filename = "examples/dataframe.csv.enc"
    config = toml.load("./pyproject.toml")["pico"]["run"]
    read_encrypted_dataframe(filename, config["PICO_CRYPTO_KEY_PIN"])

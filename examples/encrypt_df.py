"""Example 1: use device to decrypt an encrypted dataset and read into a pandas dataframe."""

import os
import time
from io import BytesIO

import pandas as pd  # type: ignore
import toml

from pico_crypto_key import CryptoKey


def encrypt_csv(crypto_key: CryptoKey, dataframe: pd.DataFrame, filename: str) -> None:
    """Encrypts a dataframe and saves to filesystem."""
    data = BytesIO()
    dataframe.to_csv(data, index=False)
    data.seek(0)

    encrypted = crypto_key.encrypt(data)

    # Write the encrypted file
    with open(filename, "wb") as fd:
        fd.write(encrypted)


def decrypt_csv(crypto_key: CryptoKey, data_file: str) -> pd.DataFrame:
    """Loads a dataframe from an encrypted csv file."""
    with open(data_file, "rb") as f:
        encrypted = BytesIO(f.read())

    data = BytesIO(crypto_key.decrypt(encrypted))
    # decryption with the wrong device will result in garbage bytes that con't be read as a dataframe
    try:
        df = pd.read_csv(data)
        return df
    except Exception as e:
        print("invalid data: %s" % e)


def main(device_path: str, device_pin: str) -> None:
    with CryptoKey(device=device_path, pin=device_pin) as crypto_key:
        ciphertext = "./examples/dataframe.csv.enc"

        # if the encrypted data isn't there create it from the plaintext
        if not os.path.isfile(ciphertext):
            plaintext = "./examples/dataframe.csv"
            dataset = pd.read_csv(plaintext)
            start = time.time()
            encrypt_csv(crypto_key, dataset, "./examples/dataframe.csv.enc")
            print("encryption took %.2fs" % (time.time() - start))

        # now decrypt
        start = time.time()
        df = decrypt_csv(crypto_key, ciphertext)
        print("decryption took %.2fs" % (time.time() - start))
        print(df)


if __name__ == "__main__":
    config = toml.load("./pyproject.toml")["pico"]["run"]

    main(config["DEVICE_SERIAL"], config["PICO_CRYPTO_KEY_PIN"])

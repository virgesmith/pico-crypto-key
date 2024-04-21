import os
from tempfile import mkstemp
from time import time
import pandas as pd

from pico_crypto_key import CryptoKey


result = pd.DataFrame(columns=["task", "size_k", "time_s", "bitrate_kbps"]).set_index(["task", "size_k"])


def hash_performance(filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with CryptoKey(pin="pico") as crypto_key:
        start = time()
        _ = crypto_key.hash(filename)
        elapsed = time() - start
        result.loc[("hash", length_k), "time_s"] = elapsed
        result.loc[("hash", length_k), "bitrate_kbps"] = length_k * 8 / elapsed


def sign_verify_performance(filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with CryptoKey(pin="pico") as crypto_key:
        start = time()
        hash, sig = crypto_key.sign(filename)
        elapsed = time() - start
        result.loc[("sign", length_k), "time_s"] = elapsed
        result.loc[("sign", length_k), "bitrate_kbps"] = length_k * 8 / elapsed

        start = time()
        pubkey = crypto_key.pubkey()
        _ = crypto_key.verify(hash, sig, pubkey)
        elapsed = time() - start
        result.loc[("verify", length_k), "time_s"] = elapsed


def encryption_performance(filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with open(filename, "rb") as fd, CryptoKey(pin="pico") as crypto_key:
        start = time()
        _ = crypto_key.encrypt(fd.read())
        elapsed = time() - start
        result.loc[("encrypt", length_k), "time_s"] = elapsed
        result.loc[("encrypt", length_k), "bitrate_kbps"] = length_k * 8 / elapsed
        fd.seek(0)
        start = time()
        _ = crypto_key.encrypt(fd.read())
        elapsed = time() - start
        result.loc[("decrypt", length_k), "time_s"] = elapsed
        result.loc[("decrypt", length_k), "bitrate_kbps"] = length_k * 8 / elapsed


if __name__ == "__main__":
    for file_size in [1024 * 10**i for i in range(4)]:
        _, filename = mkstemp()
        with open(filename, "wb") as fd:
            fd.write(os.urandom(file_size))

        hash_performance(filename)
        sign_verify_performance(filename)
        encryption_performance(filename)
        os.remove(filename)
    print(result)
    result.to_csv("performance.csv")

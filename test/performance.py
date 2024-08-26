import os
from tempfile import mkstemp
from time import time

import pandas as pd  # type: ignore[import-untyped]

from pico_crypto_key import CryptoKey

result = pd.DataFrame(columns=["task", "size_k", "time_s", "bitrate_kbps"]).set_index(["task", "size_k"])


def hash_performance(crypto_key: CryptoKey, filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    start = time()
    _ = crypto_key.hash(filename)
    elapsed = time() - start
    result.loc[("hash", length_k), "time_s"] = elapsed
    result.loc[("hash", length_k), "bitrate_kbps"] = length_k * 8 / elapsed


def sign_verify_performance(crypto_key: CryptoKey, filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    start = time()
    digest, sig = crypto_key.sign(filename)
    elapsed = time() - start
    result.loc[("sign", length_k), "time_s"] = elapsed
    result.loc[("sign", length_k), "bitrate_kbps"] = length_k * 8 / elapsed

    start = time()
    pubkey = crypto_key.pubkey()
    _ = crypto_key.verify(digest, sig, pubkey)
    elapsed = time() - start
    result.loc[("verify", length_k), "time_s"] = elapsed


def encryption_performance(crypto_key: CryptoKey, filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with open(filename, "rb") as fd:
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
    with CryptoKey() as crypto_key:
        board = crypto_key.info()[0]
        print(board)
        for file_size in [10**i for i in range(2,4)]:
            print(f"{file_size}kB")
            _, filename = mkstemp()
            with open(filename, "wb") as fd:
                fd.write(os.urandom(1024 * file_size))

            hash_performance(crypto_key, filename)
            sign_verify_performance(crypto_key, filename)
            encryption_performance(crypto_key, filename)
            os.remove(filename)
        print(result)
        result.to_csv(f"{board}-performance.csv")

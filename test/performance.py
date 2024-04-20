
import os
from time import time
from tempfile import mkstemp

from pico_crypto_key import CryptoKey

def hash_performance(filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with CryptoKey(pin="pico") as crypto_key:
        start = time()
        _ = crypto_key.hash(filename)
        elapsed = time() - start
        print(f"Hash {length_k}kB: {elapsed:.3f}s {length_k * 8 / elapsed:.0f}kbps")

def sign_verify_performance(filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with CryptoKey(pin="pico") as crypto_key:
        start = time()
        hash, sig = crypto_key.sign(filename)
        elapsed = time() - start
        print(f"Sign {length_k}kB: {elapsed:.3f}s {length_k * 8 / elapsed:.0f}kbps")

        start = time()
        pubkey = crypto_key.pubkey()
        _ = crypto_key.verify(hash, sig, pubkey)
        elapsed = time() - start
        print(f"Verify {length_k}kB: {elapsed:.3f}s")

def encryption_performance(filename: str) -> None:
    length_k = os.stat(filename).st_size / 1024
    with open(filename, "rb") as fd, CryptoKey(pin="pico") as crypto_key:
        start = time()
        _ = crypto_key.encrypt(fd.read())
        elapsed = time() - start
        print(f"Encrypt {length_k}kB: {elapsed:.3f}s {length_k * 8 / elapsed:.0f}kbps")
        fd.seek(0)
        start = time()
        _ = crypto_key.encrypt(fd.read())
        elapsed = time() - start
        print(f"Decrypt {length_k}kB: {elapsed:.3f}s {length_k * 8 / elapsed:.0f}kbps")



if __name__ == "__main__":
    for file_size in [1024 * 10 ** i for i in range(4)]:
        _, filename = mkstemp()
        with open(filename, "wb") as fd:
            fd.write(os.urandom(file_size))
        
        hash_performance(filename)
        sign_verify_performance(filename)
        encryption_performance(filename)
        os.remove(filename)

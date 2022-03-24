from hashlib import sha256
import pytest
from pico_crypto_key import CryptoKey, b64_to_hex_str
from time import sleep


@pytest.mark.parametrize("file", ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"])
def test_hash(crypto_key: CryptoKey, file: str) -> None:
    hash = b64_to_hex_str(crypto_key.hash(file))
    # print(f"[D] {hash}")

    with open(file, "rb") as fd:
      hash2 = sha256(fd.read()).hexdigest()

    # check hash matches haslib's sha256
    assert hash == hash2
    sleep(0.1)

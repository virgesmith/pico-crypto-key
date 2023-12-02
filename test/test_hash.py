from hashlib import sha256
from time import sleep

import pytest

from pico_crypto_key import CryptoKey, b64_to_hex_str


@pytest.mark.parametrize(
    "file",
    ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"],
)
def test_hash(crypto_key: CryptoKey, file: str) -> None:
    digest = b64_to_hex_str(crypto_key.hash(file))
    # print(f"[D] {hash}")

    with open(file, "rb") as fd:
        hash2 = sha256(fd.read()).hexdigest()

    # check hash matches haslib's sha256
    assert digest == hash2
    sleep(0.1)

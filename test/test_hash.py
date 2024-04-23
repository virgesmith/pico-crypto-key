from hashlib import sha256

import pytest

from pico_crypto_key import CryptoKey


@pytest.mark.parametrize(
    "file",
    ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"],
)
def test_hash(crypto_key: CryptoKey, file: str) -> None:
    digest = crypto_key.hash(file).hex()
    # print(f"[D] {hash}")

    with open(file, "rb") as fd:
        hash2 = sha256(fd.read()).hexdigest()

    # check hash matches hashlib's sha256
    assert digest == hash2

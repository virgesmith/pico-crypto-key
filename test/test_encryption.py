from io import BytesIO
import pytest
from pico_crypto_key import CryptoKey


@pytest.mark.parametrize("file", ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"])
def test_encrypt_decrypt(crypto_key: CryptoKey, file: str) -> None:
  print(f"[H] encrypt {file}")
  with open(file, "rb") as fd:
    data = BytesIO(fd.read())
    data_enc = BytesIO(crypto_key.encrypt(data))
    print("[H] decrypt encrypted data")
    data_dec = crypto_key.decrypt(data_enc)
    assert data.getbuffer() == data_dec
    print("[H] round-trip ok")

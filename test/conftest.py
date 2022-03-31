import pytest
import toml
from pico_crypto_key import CryptoKey

@pytest.fixture(scope='session')
def crypto_key() -> CryptoKey:
  config = toml.load("./pyproject.toml")["pico"]["run"]
  with CryptoKey(device=config["DEST_SERIAL"], pin=config["PICO_CRYPTO_KEY_PIN"]) as device:
    yield device


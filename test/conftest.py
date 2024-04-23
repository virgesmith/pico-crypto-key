import os
from collections.abc import Generator

import pytest

from pico_crypto_key import CryptoKey


@pytest.fixture(scope="session")
def crypto_key() -> Generator[CryptoKey, None, None]:
    assert os.getenv("PICO_CRYPTO_KEY_PIN"), "tests need PICO_CRYPTO_KEY_PIN to be set"
    with CryptoKey() as device:
        yield device

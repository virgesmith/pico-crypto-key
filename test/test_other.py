from pico_crypto_key import CryptoKey
from base64 import b64decode


def test_pubkey(crypto_key: CryptoKey) -> None:
    pubkey = b64decode(crypto_key.pubkey())
    assert len(pubkey) == 65 # ?
    assert pubkey[0] == 4 # long-form


def test_help(crypto_key: CryptoKey) -> None:
    crypto_key.help()
    # nothing to test other than no exceptions


def test_reset_init(crypto_key: CryptoKey) -> None:
    crypto_key.reset()
    crypto_key.init()
    # this will break other tests?

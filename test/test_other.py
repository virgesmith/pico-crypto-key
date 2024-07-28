from datetime import datetime, timezone

from pico_crypto_key import CryptoKey, __version__


def test_pubkey(crypto_key: CryptoKey) -> None:
    pubkey = crypto_key.pubkey()
    assert len(pubkey) == CryptoKey.ECDSA_PUBKEY_BYTES
    assert pubkey[0] in [2, 3]  # short-form ECDSA


def test_info(crypto_key: CryptoKey) -> None:
    version, timestamp = crypto_key.info()
    now = datetime.now(tz=timezone.utc)
    assert __version__ in version
    assert abs((timestamp - now).total_seconds()) < 0.01


def test_reset_init(crypto_key: CryptoKey) -> None:
    crypto_key.reset()
    crypto_key.init()
    test_pubkey(crypto_key)

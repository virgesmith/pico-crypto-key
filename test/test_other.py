from pico_crypto_key import CryptoKey


def test_pubkey(crypto_key: CryptoKey) -> None:
    pubkey = crypto_key.pubkey()
    assert len(pubkey) == 65  # ?
    assert pubkey[0] == 4  # long-form ECDSA


def test_reset_init(crypto_key: CryptoKey) -> None:
    crypto_key.reset()
    crypto_key.init()
    test_pubkey(crypto_key)

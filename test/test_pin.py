from pico_crypto_key import CryptoKey

def test_pin(crypto_key: CryptoKey) -> None:
    crypto_key._write(b"X")
    r = crypto_key._read(32)
    print(r)


if __name__ == "__main__":
    with CryptoKey() as crypto_key:
        test_pin(crypto_key)

from pico_crypto_key import CryptoKey

with CryptoKey(pin="pico") as crypto_key:
    print(crypto_key.help())
    pk = crypto_key.pubkey()
    print(pk.hex())
    print(crypto_key.hash("pico_sdk_import.cmake").hex())
    h, s = crypto_key.sign("pico_sdk_import.cmake")
    print(h.hex(), s.hex())
    print(crypto_key.verify(h, s, pk))

    plaintext = "random.bin"
    plaintext = "pico_sdk_import.cmake"
    ciphertext = plaintext + "_enc"
    decypted = plaintext + "_dec"
    with open(plaintext, "rb") as p, open(ciphertext, "wb") as c:
        c.write(crypto_key.encrypt(p.read()))

    with open(ciphertext, "rb") as p, open(decypted, "wb") as c:
        c.write(crypto_key.decrypt(p.read()))

    assert crypto_key.hash(plaintext) == crypto_key.hash(decypted)

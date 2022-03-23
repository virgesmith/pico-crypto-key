from hashlib import sha256
from pico_crypto_key import CryptoKey, b64_to_hex_str

def main(device: CryptoKey, file: str) -> None:

    print("[H] hash %s" % file)
    hash = b64_to_hex_str(device.hash(file))
    print("[D] " + hash)

    with open(file, "rb") as fd:
      hash2 = sha256(fd.read()).hexdigest()

    # check hash matches haslib's sha256
    assert hash == hash2

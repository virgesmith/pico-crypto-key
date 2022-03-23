from io import BytesIO
from pico_crypto_key import CryptoKey

def main(device: CryptoKey, file: str) -> None:
  encrypted_file = file + ".enc"
  print("[H] encrypt %s" % file)
  with open(file, "rb") as fd:
    data = BytesIO(fd.read())
    data_enc = BytesIO(device.encrypt(data))
    print("[H] decrypt encrypted data")
    data_dec = device.decrypt(data_enc)
    assert data.getbuffer() == data_dec
    print("[H] round-trip ok")


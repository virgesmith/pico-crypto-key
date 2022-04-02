"""Example 2: Use device to sign a dataset, returning (in json format) the hash, signature and public key (as hex strings) for verification."""

import time
import json
import toml
from pico_crypto_key import CryptoKey, b64_to_hex_str


def sign_data(device: CryptoKey, filename: str) -> dict:

  result = { "file": filename }

  digest, sig = device.sign(filename)
  pubkey = device.pubkey()

  # ensure it verifies
  assert device.verify(digest, sig, pubkey) == 0

  result["hash"] = b64_to_hex_str(digest)
  result["sig"] = b64_to_hex_str(sig)
  result["pubkey"] = b64_to_hex_str(pubkey)
  return result


def main(device_path: str, device_pin: str) -> None:

  with CryptoKey(device=device_path, pin=device_pin) as device:

    filename = "./examples/dataframe.csv"

    start = time.time()
    result = sign_data(device, filename)
    print("signing/verifying took %.2fs" % (time.time() - start))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
  config = toml.load("./pyproject.toml")["pico"]["run"]

  main(config["DEVICE_SERIAL"], config["PICO_CRYPTO_KEY_PIN"])

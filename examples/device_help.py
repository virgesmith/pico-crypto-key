"""Example 0: print the device "API" help."""

import toml
from pico_crypto_key import CryptoKey

if __name__ == "__main__":
  config = toml.load("./pyproject.toml")["pico"]["run"]

  with CryptoKey(device=config["DEVICE_SERIAL"], pin=config["PICO_CRYPTO_KEY_PIN"]) as crypto_key:
    crypto_key.help()


"""
Example 0: print the device "API" help
"""

import toml
from pico_crypto_key import CryptoKey

if __name__ == "__main__":
  config = toml.load("./config.toml")["run"]

  # d=Device(device=config["DEST_SERIAL"], pin=config["PICO_CRYPTO_KEY_PIN"])
  # d.__enter__()
  # d.help()

  with CryptoKey(device=config["DEST_SERIAL"], pin=config["PICO_CRYPTO_KEY_PIN"]) as crypto_key:
    #print(crypto_key)
    crypto_key.help()


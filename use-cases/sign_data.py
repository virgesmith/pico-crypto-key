# use case 2:
# use device to sign a dataset, returning (in json format) the hash, signature and public key (as hex strings) for verification

import sys
sys.path.append(".")

import os
from crypto_device import Device, b64_to_hex_str
import time
import json

device = Device("/dev/ttyACM0")

def sign_data(filename):

  result = { "file": filename }

  hash, sig = device.sign(filename)
  pubkey = device.pubkey()

  # ensure it verifies
  assert device.verify(hash, sig, pubkey) == 0

  result["hash"] = b64_to_hex_str(hash)
  result["sig"] = b64_to_hex_str(sig)
  result["pubkey"] = b64_to_hex_str(pubkey)
  return result


filename = "./use-cases/dataframe.csv"

start = time.time()
result = sign_data(filename)
print("signing/verifying took %.2fs" % (time.time() - start))

print(json.dumps(result, indent=2))


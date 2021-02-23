# use case 3:
# use a second device to verify a signature of a dataset, given a public key (as hex strings)

import os
from crypto_device import Device, b64_to_hex_str, hex_str_to_b64
import time
import json

device = Device("/dev/ttyACM0")

def verify_data(filename, signature):

  device_pubkey = b64_to_hex_str(device.pubkey())
  if device_pubkey == signature["pubkey"]:
    print("verifying device is the same as signing device")
  else:
    print("verifying device is NOT the signing device (which is good)")

  # first check our data hash is as expected
  hash = device.hash(filename)
  #print(hex_str_to_b64(signature["hash"]), hash)
  if hex_str_to_b64(signature["hash"]) != hash:
    return (False, "invalid hash")

  sig = hex_str_to_b64(signature["sig"])
  pubkey = hex_str_to_b64(signature["pubkey"])

  # ensure it verifies
  result = device.verify(hash, sig, pubkey)
  return result == 0, result


filename = "./use-cases/dataframe.csv"
signature = {
  "file": "./use-cases/dataframe.csv",
  "hash": "28d839df69762085f8ac7b360cd5ee0435030247143260cfaff0b313f99a251c",
  "sig": "304602210089d4bc103d00e2e23f0a911444b2a472a7950c74dbf69c3e2f0268b1207ca248022100fe38989e486cf2a2a8c13844d8a1647674b3d641ee4d29a73e8138db31c9ed90",
  "pubkey": "0486bb625d67b45d82c7b3cc087984abea8d4acc5d1fb70691387594f167929892e147364318d4ce2d2eefec134fa1d531a7e7b2421d945bb563bd4d115aeb7178"
}

start = time.time()
result, error = verify_data(filename, signature)
print("hashing/verifying took %.2fs" % (time.time() - start))
print("verified:", result)


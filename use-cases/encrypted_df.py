# use case 1:
# use device to decrypt an encrypted dataset and read into a pandas dataframe

import os
import pandas as pd
from io import BytesIO
from crypto_device import Device
import time

device = Device("/dev/ttyACM0")

def encrypt_csv(dataframe, filename):
  """ Encrypts a dataframe and saves to filesystem """
  data = BytesIO()
  dataframe.to_csv(data, index=False)
  data.seek(0)

  encrypted = device.encrypt(data)

  # Write the encrypted file
  with open(filename, 'wb') as fd:
    fd.write(encrypted)

def decrypt_csv(data_file):
  """ Loads a dataframe from an encrypted csv file """
  with open(data_file, 'rb') as f:
    encrypted = BytesIO(f.read())

  data = BytesIO(device.decrypt(encrypted))
  # decryption with the wrong device will result in garbage bytes that con't be read as a dataframe
  try:
    df = pd.read_csv(data)
    return df
  except Exception as e:
    print("invalid data: %s" % e)

ciphertext = "./use-cases/dataframe.csv.enc"

# if the encrypted data isn't there create it from the plaintext
if not os.path.isfile(ciphertext):
  plaintext = "./use-cases/dataframe.csv"
  dataset = pd.read_csv(plaintext)
  start = time.time()
  encrypt_csv(dataset, "./use-cases/dataframe.csv.enc")
  print("encryption took %.2fs" % (time.time() - start))

# now decrypt
start = time.time()
df = decrypt_csv(ciphertext)
print("decryption took %.2fs" % (time.time() - start))
print(df)

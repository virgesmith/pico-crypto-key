import sys
from crypto_device import Device, b64_to_hex_str

CHUNK_SIZE = 16384

wrong_hash = b'S1L93ZmizMM7zScSFiQDqdWzF3FYj0SACivbiiY/Bdk='
wrong_sig = b'MEQCIFSHjtLevnv268DYt57j0zbXThO/RtpxBC6kaW6a1B2aAiBl71b4mEH5yUMGkPpMwFAF/XZ+2//LABB0puHi19HvKg=='
wrong_pubkey = b'BPqvnhfp83ao7n2oWpwIPBW2TBH6LylpG32Rab10n0qUXjzJ4cLdaZY2+n94KQ7PZsvx+iigW62xL/vru2D0Jn4='


def main(device, file):
  pubkey = device.pubkey()
  print("[D] pubkey: %s" % b64_to_hex_str(pubkey))

  print("[H] sign %s" % file)
  hash, sig = device.sign(file)
  print("[D] hash: " + b64_to_hex_str(hash))
  print("[D] sig: %s" % b64_to_hex_str(sig))

  err_code = device.verify(hash, sig, pubkey)
  assert err_code == 0
  print("[D] verify: %s" % err_code)

  # wrong hash
  err_code = device.verify(wrong_hash, sig, pubkey)
  assert err_code == -19968 # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED
  print("[D] wrong hash verify: %s" % err_code)

  # wrong sig
  err_code = device.verify(hash, wrong_sig, pubkey)
  assert err_code == -19968 # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED
  print("[D] wrong sig verify: %s" % err_code)

  # wrong pubkey
  err_code = device.verify(hash, sig, wrong_pubkey)
  assert err_code == -19968 # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED
  print("[D] wrong pubkey verify: %s" % err_code)

if __name__ == "__main__":
  device = Device("/dev/ttyACM0")
  assert len(sys.argv) == 2
  #try:
  main(device, sys.argv[1])
  #except Exception as e:
  #  print(e)


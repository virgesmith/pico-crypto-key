import pytest
from pico_crypto_key import CryptoKey, b64_to_hex_str

wrong_hash = b'S1L93ZmizMM7zScSFiQDqdWzF3FYj0SACivbiiY/Bdk='
wrong_sig = b'MEQCIFSHjtLevnv268DYt57j0zbXThO/RtpxBC6kaW6a1B2aAiBl71b4mEH5yUMGkPpMwFAF/XZ+2//LABB0puHi19HvKg=='
wrong_pubkey = b'BPqvnhfp83ao7n2oWpwIPBW2TBH6LylpG32Rab10n0qUXjzJ4cLdaZY2+n94KQ7PZsvx+iigW62xL/vru2D0Jn4='


@pytest.mark.parametrize("file", ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"])
def test_sign_verify(crypto_key: CryptoKey, file: str) -> None:
  pubkey = crypto_key.pubkey()
  print("[D] pubkey: %s" % b64_to_hex_str(pubkey))

  print("[H] sign %s" % file)
  digest, sig = crypto_key.sign(file)
  print("[D] hash: " + b64_to_hex_str(digest))
  print("[D] sig: %s" % b64_to_hex_str(sig))

  err_code = crypto_key.verify(digest, sig, pubkey)
  assert err_code == 0
  print("[D] verify: %s" % err_code)

  # wrong hash
  err_code = crypto_key.verify(wrong_hash, sig, pubkey)
  assert err_code == -19968 # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED
  print("[D] wrong hash verify: %s" % err_code)

  # wrong sig
  err_code = crypto_key.verify(digest, wrong_sig, pubkey)
  assert err_code == -19968 # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED
  print("[D] wrong sig verify: %s" % err_code)

  # wrong pubkey
  err_code = crypto_key.verify(digest, sig, wrong_pubkey)
  assert err_code == -19968 # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED
  print("[D] wrong pubkey verify: %s" % err_code)




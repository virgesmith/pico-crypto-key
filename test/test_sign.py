from hashlib import sha256

import ecdsa
import pytest

from pico_crypto_key import CryptoKey

wrong_hash = bytes.fromhex("4b52fddd99a2ccc33bcd2712162403a9d5b31771588f44800a2bdb8a263f05d9")
wrong_sig = bytes.fromhex(
    "3044022054878ed2debe7bf6ebc0d8b79ee3d336d74e13bf46da71042ea4696e9ad41d9a022065ef56f89841f9c9430690fa4cc05005fd767edbffcb001074a6e1e2d7d1ef2a"
)
wrong_pubkey = bytes.fromhex(
    "04faaf9e17e9f376a8ee7da85a9c083c15b64c11fa2f29691b7d9169bd749f4a945e3cc9e1c2dd699636fa7f78290ecf66cbf1fa28a05badb12ffbebbb60f4267e"
)


@pytest.mark.parametrize(
    "file",
    ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"],
)
def test_sign_verify(crypto_key: CryptoKey, file: str) -> None:
    pubkey = crypto_key.pubkey()
    digest, sig = crypto_key.sign(file)

    err_code = crypto_key.verify(digest, sig, pubkey)
    assert not err_code

    with open(file, "rb") as fd:
        content = fd.read()
        # check it verifies using a 3rdparty library
        verifying_key = ecdsa.VerifyingKey.from_string(crypto_key.pubkey(), curve=ecdsa.SECP256k1, hashfunc=sha256)
        assert verifying_key.verify(sig, content, sigdecode=ecdsa.util.sigdecode_der)

        # wrong hash
        err_code = crypto_key.verify(wrong_hash, sig, pubkey)
        assert err_code == CryptoKey.VERIFY_FAILED
        # 3rd party
        with pytest.raises(ecdsa.keys.BadSignatureError):
            verifying_key.verify_digest(sig, wrong_hash, sigdecode=ecdsa.util.sigdecode_der)

        # wrong sig
        err_code = crypto_key.verify(digest, wrong_sig, pubkey)
        assert err_code == CryptoKey.VERIFY_FAILED
        # 3rd party
        with pytest.raises(ecdsa.keys.BadSignatureError):
            verifying_key.verify(wrong_sig, content, sigdecode=ecdsa.util.sigdecode_der)

        # wrong pubkey
        err_code = crypto_key.verify(digest, sig, wrong_pubkey)
        assert err_code == CryptoKey.VERIFY_FAILED
        # 3rd party
        verifying_key = ecdsa.VerifyingKey.from_string(wrong_pubkey, curve=ecdsa.SECP256k1, hashfunc=sha256)
        with pytest.raises(ecdsa.keys.BadSignatureError):
            verifying_key.verify(wrong_sig, content, sigdecode=ecdsa.util.sigdecode_der)

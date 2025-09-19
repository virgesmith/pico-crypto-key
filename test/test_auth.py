"""
Example: change the device pin.
"""

import struct
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256

import ecdsa  # type: ignore[import-untyped]
import pytest

from pico_crypto_key import CryptoKey, timestamp


@pytest.mark.parametrize("challenge", [b"testing", b""])
def test_pubkey(crypto_key: CryptoKey, challenge: bytes) -> None:
    rp = "example.com"
    user = "a.user"

    pubkey = crypto_key.register(rp, user)

    # check keygen is consistent
    assert pubkey == crypto_key.register(rp, user)
    assert pubkey != crypto_key.register("other.org", user)

    sig = b64decode(crypto_key.auth(rp, user, challenge))

    # use 3rdparty lib to verify
    verifying_key = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1, hashfunc=sha256)

    timestamped_challenge = challenge + timestamp()
    assert verifying_key.verify(sig, timestamped_challenge, sigdecode=ecdsa.util.sigdecode_der)

    # the device's main pubkey doesnt work
    wrong_key = ecdsa.VerifyingKey.from_string(crypto_key.pubkey(), curve=ecdsa.SECP256k1, hashfunc=sha256)
    with pytest.raises(ecdsa.keys.BadSignatureError):
        wrong_key.verify(sig, timestamped_challenge, sigdecode=ecdsa.util.sigdecode_der)

    t = int((datetime.now(tz=timezone.utc).timestamp() - 60) * 1000)
    expired_challenge = challenge + struct.pack("Q", t - 60000)
    with pytest.raises(ecdsa.keys.BadSignatureError):
        verifying_key.verify(sig, expired_challenge, sigdecode=ecdsa.util.sigdecode_der)

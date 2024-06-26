"""
Example: change the device pin.
"""

import struct
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256

import ecdsa
import pytest

from pico_crypto_key import CryptoKey


@pytest.mark.parametrize("challenge", [b"testing", b""])
def test_pubkey(crypto_key: CryptoKey, challenge: bytes) -> None:
    rp = "example.com"

    pubkey = crypto_key.register(rp)

    # check keygen is consistent
    assert pubkey == crypto_key.register(rp)
    assert pubkey != crypto_key.register("other.org")

    now = datetime.now(tz=timezone.utc)
    sig = b64decode(crypto_key.auth(rp, challenge))

    t = int(now.timestamp() * 1000)
    t = t - t % 60000

    # use 3rdparty lib to verify
    verifying_key = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1, hashfunc=sha256)

    timestamped_challenge = challenge + struct.pack("Q", t)
    assert verifying_key.verify(sig, timestamped_challenge, sigdecode=ecdsa.util.sigdecode_der)

    # the device's main pubkey doesnt work
    wrong_key = ecdsa.VerifyingKey.from_string(crypto_key.pubkey(), curve=ecdsa.SECP256k1, hashfunc=sha256)
    with pytest.raises(ecdsa.keys.BadSignatureError):
        wrong_key.verify(sig, timestamped_challenge, sigdecode=ecdsa.util.sigdecode_der)

    expired_challenge = challenge + struct.pack("Q", t - 60000)
    with pytest.raises(ecdsa.keys.BadSignatureError):
        verifying_key.verify(sig, expired_challenge, sigdecode=ecdsa.util.sigdecode_der)

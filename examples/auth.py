"""
Example: change the device pin.
"""

import struct
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256

import ecdsa

from pico_crypto_key import CryptoKey


def auth() -> None:
    with CryptoKey() as crypto_key:
        now = datetime.now(tz=timezone.utc)
        _, timestamp = crypto_key.info()
        print(f"Host-device time diff: {(now - timestamp).total_seconds()}s")

        challenge = b"testing time-based auth"
        print(f"challenge is: {challenge}")
        response = crypto_key.auth(challenge)
        print(f"response is: {response}")
        sig = b64decode(response)

        # check it verifies using a 3rdparty library
        verifying_key = ecdsa.VerifyingKey.from_string(crypto_key.pubkey(), curve=ecdsa.SECP256k1, hashfunc=sha256)

        # append rounded timestamp to challenge
        t = int(now.timestamp() * 1000)
        challenge += struct.pack("Q", t - t % 60000)
        try:
            result = verifying_key.verify(sig, challenge, sigdecode=ecdsa.util.sigdecode_der)
            print(f"Verified: {result}")
        except ecdsa.keys.BadSignatureError:
            print("Verified: False")


if __name__ == "__main__":
    auth()

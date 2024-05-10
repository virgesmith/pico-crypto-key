"""
Example: change the device pin.
"""

import struct
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256

import ecdsa

from pico_crypto_key import CryptoKey, CryptoKeyNotFoundError


def auth() -> None:
    try:
        with CryptoKey() as crypto_key:
            now = datetime.now(tz=timezone.utc)
            _, timestamp = crypto_key.info()
            print(f"Host-device time diff: {(now - timestamp).total_seconds()}s")

            rps = ["example.com", "another.org"]

            pubkeys = [crypto_key.register(rp) for rp in rps]

            for rp, pk in zip(rps, pubkeys, strict=True):
                print(f"registered {rp}: {pk.hex()}")

            challenge = b"testing time-based auth"
            print(f"challenge is: {challenge}")
            responses = [crypto_key.auth(rp, challenge) for rp in rps]

            for rp, token in zip(rps, responses, strict=True):
                print(f"auth response {rp}: {token}")

            # check it verifies using a 3rdparty library
            vks = [ecdsa.VerifyingKey.from_string(pk, curve=ecdsa.SECP256k1, hashfunc=sha256) for pk in pubkeys]

            # append rounded timestamp to challenge
            t = int(now.timestamp() * 1000)
            challenge += struct.pack("Q", t - t % 60000)
            for rp, vk, token in zip(rps, vks, responses, strict=True):
                try:
                    result = vk.verify(b64decode(token), challenge, sigdecode=ecdsa.util.sigdecode_der)
                    print(f"{rp} verified: {result}")
                except ecdsa.keys.BadSignatureError:
                    print("{rp} verified: False")

            # one RP cannot verify tokens for a different RP
            for i in range(2):
                try:
                    vks[i].verify(b64decode(responses[1 - i]), challenge, sigdecode=ecdsa.util.sigdecode_der)
                except ecdsa.keys.BadSignatureError:
                    print(f"{rps[i]} cannot verify {responses[i-1]}")
                else:
                    raise RuntimeError(f"{rps[i]} verified {responses[i-1]}, this should not happen")

    except CryptoKeyNotFoundError:
        print("Key not connected")


if __name__ == "__main__":
    auth()

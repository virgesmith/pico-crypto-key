"""
Example: change the device pin.
"""

from datetime import datetime, timezone
import struct
import hashlib

from pico_crypto_key import CryptoKey


def auth() -> None:
    with CryptoKey() as crypto_key:
        now = datetime.now(tz=timezone.utc)
        _, timestamp = crypto_key.info()
        print(f"Time diff: {(now - timestamp).total_seconds()}s")

        challenge = b"hello"
        sig = crypto_key.auth(challenge)

        t = int(now.timestamp() * 1000)
        t = t - t % 60000

        print(len(sig))

        hash = hashlib.sha256(challenge + struct.pack("Q", t)).digest()
        print(hash.hex())
        print(sig.hex())

        verified = crypto_key.verify(hash, sig, crypto_key.pubkey())
        print(verified)

        # hashes (timestamp) won't match
        oldsig = bytes.fromhex("3045022100ebf6a891cf1b8966b91c107fcd048256140f92f27d9a45f435f749fed7c91ed802206a44771136a66380b83deae7d92a4237a6b31a9998694240c14fa55d49f9e317")
        verified = crypto_key.verify(hash, oldsig, crypto_key.pubkey())
        print(verified)

        # hashes (challenge) won't match
        hash = hashlib.sha256(b"bonjour" + struct.pack("Q", t)).digest()
        verified = crypto_key.verify(hash, oldsig, crypto_key.pubkey())
        print(verified)


if __name__ == "__main__":
    auth()

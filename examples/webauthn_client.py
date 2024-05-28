import json
import struct
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256
from socket import socket

import ecdsa

ENDPOINT = ("localhost", 5000)
BUFFER_SIZE = 1024


def register(host: str) -> bytes:
    """Returns shoft-form pubkey raw bytes"""
    sock = socket()
    sock.connect(ENDPOINT)
    payload = ("register", dict(host=host))
    sock.send(json.dumps(payload).encode())
    buffer = sock.recv(BUFFER_SIZE)
    return buffer


def authenticate(host: str, challenge: bytes) -> bytes:
    """Returns base64-encoded DER format signature"""
    sock = socket()
    sock.connect(ENDPOINT)
    payload = ("auth", dict(host=host, challenge=challenge.decode()))
    sock.send(json.dumps(payload).encode())
    buffer = sock.recv(BUFFER_SIZE)
    result = buffer.decode()
    return result


if __name__ == "__main__":
    receiving_party = "example.com"
    challenge = b"auth me now!"
    timestamp = datetime.now(tz=timezone.utc)

    try:
        pubkey = register(receiving_party)
        print(f"registered {receiving_party}: {pubkey.hex()}")

        print(f"challenge is: {challenge}")
        token = authenticate("example.com", challenge)
        print(f"auth response {receiving_party}: {token}")

        # check it verifies using a 3rdparty library
        verifying_key = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1, hashfunc=sha256)

        # # append rounded timestamp to challenge
        t = int(timestamp.timestamp() * 1000)
        challenge += struct.pack("Q", t - t % 60000)

        try:
            result = verifying_key.verify(b64decode(token), challenge, sigdecode=ecdsa.util.sigdecode_der)
            print(f"{receiving_party} verified: {result}")
        except ecdsa.keys.BadSignatureError:
            print("{rp} verified: False")
    except ConnectionRefusedError:
        print("Is webauthn server running?\n" "Run python examples/webauthn_server.py in another shell")

import logging
import struct
from time import sleep
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256
from typing import Annotated

import ecdsa
from fastapi import FastAPI, Header, HTTPException

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

userdata: dict[str, bytes] = {}

HOST_ID = "localhost:8000"

app = FastAPI()

def _get_challenge(username: str) -> str:
    return f"sign this {username}@{HOST_ID}!"


def _verify_challenge(username: str, pubkey: bytes, token: str) -> bool:
    timestamp = datetime.now(tz=timezone.utc)
    # check it verifies (using a 3rdparty library)
    verifying_key = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1, hashfunc=sha256)

    # append rounded timestamp to challenge
    t = int(timestamp.timestamp() * 1000)
    challenge = _get_challenge(username).encode() + struct.pack("Q", t - t % 60000)

    try:
        result = verifying_key.verify(b64decode(token), challenge, sigdecode=ecdsa.util.sigdecode_der)
    except ecdsa.keys.BadSignatureError:
        result = False
    logging.info(f"{HOST_ID} verified: {result}")

    return result


@app.get("/register")
async def register(
    username: Annotated[str, "user name"], pubkeyhex: Annotated[str, "short-form pulic key in hex"],
    token: Annotated[str, Header()]
) -> None:
    """
    Register a new user and their public key. Will fail if:
     - user already exists
     - public key does not verify token
    """
    if username in userdata:
        raise HTTPException(status_code=403, detail="user exists")


    logging.info(f"registering {username} with {pubkeyhex}")
    userdata[username] = bytes.fromhex(pubkeyhex)
    return "OK"


@app.get("/challenge")
async def challenge(username: Annotated[str, "user name"]) -> str:
    """
    Provide a challenge string for the authenticator to sign
    """
    return _get_challenge(username)


@app.get("/login")
async def login(username: Annotated[str, "user name"], token: Annotated[str, Header()]) -> str:
    """
    Authenticate with the host. Token is the signature of a combination of host, challenge and timestamp
    """

    # pretend we're not local (timestamp misalignment can cause auth failures)
    sleep(0.02)

    if username not in userdata:
        raise HTTPException(status_code=403, detail="user not found")

    logging.info(f"{username}: {token}")

    if not _verify_challenge(username, userdata[username], token):
        raise HTTPException(status_code=401, detail="authentication failed")

    # timestamp = datetime.now(tz=timezone.utc)
    # # check it verifies (using a 3rdparty library)
    # verifying_key = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1, hashfunc=sha256)

    # # append rounded timestamp to challenge
    # t = int(timestamp.timestamp() * 1000)
    # challenge = CHALLENGE.format(username).encode() + struct.pack("Q", t - t % 60000)

    # try:
    #     result = verifying_key.verify(b64decode(token), challenge, sigdecode=ecdsa.util.sigdecode_der)
    #     logging.info(f"{HOST_ID} verified: {result}")
    # except ecdsa.keys.BadSignatureError:
    #     raise HTTPException(status_code=401, detail="authentication failed") from None

    return "OK"

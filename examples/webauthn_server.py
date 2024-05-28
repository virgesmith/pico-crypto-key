import json
import logging
import socket
from datetime import datetime, timezone

from pico_crypto_key.device import CryptoKey

ENDPOINT = ("localhost", 5000)

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


def serve(key: CryptoKey):
    logging.info(f"listening for requests on {ENDPOINT[0]}:{ENDPOINT[1]}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(ENDPOINT)
        sock.listen(5)
        while True:
            client_socket, client_name = sock.accept()
            command, payload = json.loads(client_socket.recv(1024).decode("utf-8"))
            logging.info(f"{client_name[0]} requests {command}:{payload}")
            host = payload["host"]
            if command == "register":
                pubkey = key.register(host)
                logging.info(f"registering with {host}: {pubkey.hex()}")
                client_socket.send(pubkey)
            elif command == "auth":
                _, timestamp = key.info()
                now = datetime.now(tz=timezone.utc)
                logging.info(f"Host-device time diff: {(now - timestamp).total_seconds()}s")
                # convert str back to bytes (json doesn't allow bytes)
                challenge = payload["challenge"].encode()
                token = key.auth(host, challenge)
                logging.info(f"authing with {host} challenge={challenge} response={token}")
                client_socket.send(token)
            else:
                client_socket.send(json.dumps({"ERROR": f"{payload} not understood"}).encode())
    except KeyboardInterrupt:
        logging.info("interrupted")
    finally:
        logging.info("closing socket")
        sock.close()


if __name__ == "__main__":
    with CryptoKey() as key:
        version, timestamp = key.info()
        logging.info(f"{version} @ {timestamp}")
        serve(key)

"""Example 3: Use a second device to verify a signature of a dataset, given a public key (as hex strings)."""

import time

import toml

from pico_crypto_key import CryptoKey, b64_to_hex_str, hex_str_to_b64


def verify_data(device: CryptoKey, signature_data: dict[str, str]) -> bool:

    device_pubkey = b64_to_hex_str(device.pubkey())
    if device_pubkey == signature_data["pubkey"]:
        print("verifying device is the same as signing device")
    else:
        print("verifying device is NOT the signing device (which is good)")

    # first check our data hash is as expected
    digest = device.hash(signature_data["file"])
    # print(hex_str_to_b64(signature["hash"]), hash)
    if hex_str_to_b64(signature_data["hash"]) != digest:
        raise RuntimeError("invalid hash")

    sig = hex_str_to_b64(signature_data["sig"])
    pubkey = hex_str_to_b64(signature_data["pubkey"])

    # ensure it verifies
    result = device.verify(digest, sig, pubkey)
    return result == 0


def main(device_path: str, device_pin: str) -> None:

    signature = {
        "file": "./examples/dataframe.csv",
        "hash": "28d839df69762085f8ac7b360cd5ee0435030247143260cfaff0b313f99a251c",
        "sig": "304602210089d4bc103d00e2e23f0a911444b2a472a7950c74dbf69c3e2f0268b1207ca248022100fe38989e486cf2a2a8c13844d8a1647674b3d641ee4d29a73e8138db31c9ed90",
        "pubkey": "0486bb625d67b45d82c7b3cc087984abea8d4acc5d1fb70691387594f167929892e147364318d4ce2d2eefec134fa1d531a7e7b2421d945bb563bd4d115aeb7178",
    }

    with CryptoKey(device=device_path, pin=device_pin) as device:

        start = time.time()
        result = verify_data(device, signature)

        print("hashing/verifying took %.2fs" % (time.time() - start))
        print("verified:", result)


if __name__ == "__main__":
    config = toml.load("./pyproject.toml")["pico"]["run"]

    main(config["DEVICE_SERIAL"], config["PICO_CRYPTO_KEY_PIN"])

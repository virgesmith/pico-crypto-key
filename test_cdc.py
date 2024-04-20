import os
from time import time
import usb.core
import usb.util
from struct import pack, unpack

CHUNK_SIZE = 2048

def get_endpoints(device: usb.core.Device) -> tuple:
    # TODO this function needs improvement
    cfg = device.get_active_configuration()
    # usb.core.USBError: [Errno 13] Access denied (insufficient permissions)
    # see https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the

    interface = cfg[(1, 0)]

    endpoints = usb.util.find_descriptor(
        interface,
        find_all=True,
        # match the first OUT endpoint
        # custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == 0x02
    )
    # print([ep for ep in endpoints])

    return endpoints

# def dprint(endpoint_out) -> None:
#     response = endpoint_out.read(CHUNK_SIZE)
#     print(response.tobytes().decode())


def main(device) -> None:
    endpoint_in, endpoint_out = get_endpoints(device)

    reattach = False
    if device.is_kernel_driver_active(0):
        reattach = True
        device.detach_kernel_driver(0)

    print("H: sending pin")
    endpoint_in.write(b"pick")
    response = endpoint_out.read(4).tobytes()
    print(f"H: got '{response}' ({len(response)})")

    # public key
    endpoint_in.write(b"k")
    pubkey = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got ({len(pubkey)}) {pubkey.hex()}")

    # filename = "build/pico-crypto-key.dis" 
    filename = "random.bin" 

    # hash
    start = time()
    endpoint_in.write(b"h")
    file_length = os.stat(filename).st_size
    uint32 = pack("I", file_length)   
    ret = endpoint_in.write(uint32)
    print(f"H: wrote {ret} bytes")
    with open(filename, "rb") as fd:
        write_remaining = file_length
        while write_remaining > 0:
            write_chunk_length = min(write_remaining, CHUNK_SIZE)
            # write a chunk
            data = fd.read(write_chunk_length)
            ret = endpoint_in.write(data)
            write_remaining -= ret    
    print(f"H: wrote {file_length} bytes")
    response = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got ({len(response)}) {response.hex()}")
    elapsed = time() - start
    print(f"hash rate {file_length / 1024 / elapsed:.1f}kpbs")

    # sign
    start = time()
    endpoint_in.write(b"s")
    file_length = os.stat(filename).st_size
    uint32 = pack("I", file_length)   
    ret = endpoint_in.write(uint32)
    print(f"H: wrote {ret} bytes")
    with open(filename, "rb") as fd:
        write_remaining = file_length
        while write_remaining > 0:
            write_chunk_length = min(write_remaining, CHUNK_SIZE)
            # write a chunk
            data = fd.read(write_chunk_length)
            ret = endpoint_in.write(data)
            write_remaining -= ret    
    print(f"H: wrote {file_length} bytes")
    hash = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got ({len(hash)}) {hash.hex()}")
    sig = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got ({len(sig)}) {sig.hex()}")
    elapsed = time() - start
    print(f"sign rate {file_length / 1024 / elapsed:.1f}kpbs")

    # verify
    start = time()
    endpoint_in.write(b"v")
    ret = endpoint_in.write(hash)
    print(f"H: wrote {ret}")

    uint32 = pack("I", len(sig)) 
    ret = endpoint_in.write(uint32)
    print(f"H: wrote {ret}")
    ret = endpoint_in.write(sig)
    print(f"H: wrote {ret}")

    uint32 = pack("I", len(pubkey))   
    ret = endpoint_in.write(uint32)
    print(f"H: wrote {ret}")
    ret = endpoint_in.write(pubkey)
    print(f"H: wrote {ret}")

    uint32 = endpoint_out.read(4).tobytes()
    result = unpack("I", uint32)
    print(f"H: got {result}")
    elapsed = time() - start
    print(f"verify time {elapsed * 1000:.1f}ms")

    # encrypt
    start = time()
    endpoint_in.write(b"e")
    plaintext_filename = "random.bin" 
    encrypted_filename = plaintext_filename + "_enc"
    file_length = os.stat(plaintext_filename).st_size
    uint32 = pack("I", file_length)   
    ret = endpoint_in.write(uint32)
    print(f"H: wrote {ret} bytes")
    with open(plaintext_filename, "rb") as pd, open(encrypted_filename, "wb") as cd:
        write_remaining = file_length
        read_remaining = file_length
        while write_remaining > 0:
            write_chunk_length = min(write_remaining, CHUNK_SIZE)
            # write a chunk
            data = pd.read(write_chunk_length)
            bytes_written = endpoint_in.write(data)
            print(f"H: wrote {bytes_written}")
            write_remaining -= bytes_written
    
            # read an encrypted chunk
            # TODO why fail if we only ask for bytes written?
            data = endpoint_out.read(read_remaining).tobytes()
            bytes_read = len(data)
            print(f"H: read {bytes_read}")
            cd.write(data) 
            read_remaining -= bytes_read

    elapsed = time() - start
    print(f"encrypt time {elapsed * 1000:.1f}ms")

    # decrypt
    decrypted_filename = plaintext_filename + "_dec" 
    start = time()
    endpoint_in.write(b"d")
    file_length = os.stat(encrypted_filename).st_size
    uint32 = pack("I", file_length)   
    ret = endpoint_in.write(uint32)
    print(f"H: wrote {ret} bytes")
    with open(encrypted_filename, "rb") as cd, open(decrypted_filename, "wb") as pd:
        write_remaining = file_length
        read_remaining = file_length
        while read_remaining > 0:
            write_chunk_length = min(write_remaining, CHUNK_SIZE)
            # write a chunk
            data = cd.read(write_chunk_length)
            bytes_written = endpoint_in.write(data)
            print(f"H: wrote {bytes_written}")
            write_remaining -= bytes_written
    
            # read an decrypted chunk
            # TODO why fail if we only ask for bytes written?
            data = endpoint_out.read(read_remaining).tobytes()
            bytes_read = len(data)
            print(f"H: read {bytes_read}")
            pd.write(data) 
            read_remaining -= bytes_read
    elapsed = time() - start
    print(f"decrypt time {elapsed * 1000:.1f}ms")

    # reset the repl
    endpoint_in.write(b"r")

    usb.util.dispose_resources(device)

    # It may raise USBError if there's e.g. no kernel driver loaded at all
    if reattach:
        device.attach_kernel_driver(0)
    


if __name__ == "__main__":
    try:
        device = usb.core.find(idVendor=0xAAFE, idProduct=0xC0FF)
        main(device)
    except:
        device.reset()
        raise

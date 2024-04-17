import os
from time import time
import usb.core
import usb.util
from struct import pack
import hashlib

CHUNK_SIZE = 16384

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

def dprint(endpoint_out) -> None:
    response = endpoint_out.read(CHUNK_SIZE)
    print(response.tobytes().decode())


def main() -> None:
    device = usb.core.find(idVendor=0xAAFE, idProduct=0xC0FF)
    endpoint_in, endpoint_out = get_endpoints(device)

    reattach = False
    if device.is_kernel_driver_active(0):
        reattach = True
        device.detach_kernel_driver(0)

    print("H: sending pin")
    endpoint_in.write("pico".encode("utf-8"))
    response = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got '{response}' ({len(response)})")

    # key
    endpoint_in.write("k".encode("utf-8"))
    response = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got ({len(response)})")
    print(response.hex())

    # hash
    endpoint_in.write("h".encode("utf-8"))
    filename = "CMakeLists.txt" 
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
            print(f"H: wrote {ret} bytes")
            write_remaining -= ret    
    response = endpoint_out.read(CHUNK_SIZE).tobytes()
    print(f"H: got ({len(response)})")
    print(response.hex())


    # reset the repl
    endpoint_in.write("r".encode("utf-8"))
    

    # start = time()
    # file_length = os.stat(filename).st_size
    # print(f"H: file is {file_length} bytes")
    # with open(filename, "rb") as in_fd, open(filename + "_processed", "wb") as out_fd:
    #     uint32 = pack("I", file_length)
    #     ret = endpoint_in.write(uint32)
    #     print(f"H: wrote {ret} bytes")
    #     dprint(endpoint_out)

    #     write_remaining = file_length
    #     read_remaining = file_length
    #     while read_remaining > 0:
    #         write_chunk_length = min(write_remaining, CHUNK_SIZE)

    #         # write a chunk
    #         data = in_fd.read(write_chunk_length)
    #         ret = endpoint_in.write(data)
    #         print(f"H: wrote {ret} bytes")
    #         write_remaining -= ret

    #         # read a chunk (ask for as much as possible)
    #         data = endpoint_out.read(read_remaining).tobytes()
    #         bytes_read = len(data)
    #         out_fd.write(data)
    #         print(f"H: read {bytes_read} bytes")
    #         read_remaining -= bytes_read

    # elapsed = time() - start
    # # 2 to account for read+write, 128 converts bytes to kilobits
    # print(f"{2 * file_length / 128 / elapsed:.1f} kbps")

    usb.util.dispose_resources(device)

    # It may raise USBError if there's e.g. no kernel driver loaded at all
    if reattach:
        device.attach_kernel_driver(0)


if __name__ == "__main__":
    main()


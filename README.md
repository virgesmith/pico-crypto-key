# pico-crypto-key

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/fb9853538e3a421d9715812f87f3269d)](https://www.codacy.com/gh/virgesmith/pico-crypto-key/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virgesmith/pico-crypto-key&amp;utm_campaign=Badge_Grade)

Using a Raspberry Pi [Pico](https://www.raspberrypi.org/products/raspberry-pi-pico/) microcontroller as a USB security device that provides:

- cryptographic hashing (SHA256)
- encryption and decryption (256 bit AES)
- public key cryptography (ECDSA - secp256k1, as Bitcoin)

I'm not a security expert and the device/software is almost certainly not hardened enough for serious use. I just did it cos it was there, and I was bored. Also, it's not fast, but that might be ok depending on your current lockdown status. Most importantly, it works. Here's some steps I took towards making it securer:

- the device is pin protected. Only the sha256 hash of the (salted) pin is stored on the device.
- the private key is only initialised once a correct pin has been entered, and is a sha256 hash of the (salted) unique device id of the Pico. So no two devices should have the same key.
- the private key never leaves the device and is stored only in volatile memory.

NB This has been tested on both Pico and Pico W boards. The latter requires a bit of extra work for the onboard LED to work.

## Update v1.3

Adds:

- Time synchronisation between host and device
- Device info: firmware version, board type, current time
- Generation of time-based authentication tokens (like Webauthn)
- Multiple build targets: Pico and Pico W. LED now works on Pico W.
- Switch to short-form public keys.

## Update v1.2

The device pin is now configurable. See [PIN protection](#pin-protection) and the [change pin](#change-pin) example.

## Update v1.1

The device now uses USB CDC rather than serial to communicate with the host which allows much faster bitrates and avoids the need to encode binary data. Performance is improved, but varies considerably by task (results are for a 1000kB input):

| task    | CDC<br>time(s) | CDC<br>bitrate(kbps) | serial<br>time(s) | serial<br>bitrate(kbps)| Speedup(%) |
|:--------|---------------:|---------------------:|------------------:|-----------------------:|-----------:|
| hash    |            2.6 |               3026.3 |              19.6 |                  407.9 |      641.9 |
| sign    |            2.8 |               2904.1 |              19.6 |                  408.3 |      611.3 |
| verify  |            0.4 |                      |               0.5 |                        |       16.0 |
| encrypt |           23.9 |                334.2 |              43.5 |                  183.8 |       81.9 |
| decrypt |           23.8 |                336.0 |              43.1 |                  185.7 |       81.0 |

## Dependencies/prerequisites

Both Pico and Pico W boards are supported. The latter requires the wifi driver purely for the LED (which is connected to the wifi chip) to function. However, neither wifi nor bluetooth are enabled.

`pico-crypto-key` is a python (dev) package that provides:

- a simplified build process
- a python interface to the device.

First, clone/fork this repo and install the package in development (editable) mode:

```sh
pip install -e .[dev]
```

If this step fails, try upgrading to a more recent version of pip.

You will then need to:

- install the compiler toolchain (arm cross-compiler) and cmake:

  ```sh
  sudo apt install gcc-arm-none-eabi cmake
  ```

- download [pico-sdk](https://github.com/raspberrypi/pico-sdk), see [here](https://www.raspberrypi.org/documentation/pico/getting-started/). NB This project uses a tagged release of pico-sdk, so download and extract e.g. [1.5.1](hhttps://github.com/raspberrypi/pico-sdk/archive/refs/tags/1.5.1.tar.gz)

- download and extract a release of [tinyusb](https://github.com/hathach/tinyusb/releases/tag/0.16.0). Replace the empty `pico-sdk-1.5.1/lib/tinyusb` directory with a symlink to where you extracted it, e.g.

  ```sh
  cd pico-sdk-1.5.1/lib
  rmdir tinyusb
  ln -s ../../tinyusb-0.16.0 tinyusb
  ```

- [**pico_w only**], repeat the above step for `cyw43-driver`, which can be found [here](https://github.com/georgerobotics/cyw43-driver)

- download [mbedtls](https://tls.mbed.org/api/): see also their [repo](https://github.com/ARMmbed/mbedtls). Currently using the 3.6.0 release/tag.

  create symlinks in the project root to the pico SDK and mbedtls, e.g.:

  ```sh
  ln -s ../pico-sdk-1.5.1 pico-sdk
  ln -s ../mbedtls-3.6.0 mbedtls
  ```

  Not sure why, but I couldn't get it to work with the symlink inside pico-sdk like tinyusb.

You should now have a structure something like this:

```txt
.
├──mbedtls-3.6.0
├──pico-crypto-key
│  ├──examples
│  ├──mbedtls -> ../mbedtls-3.6.0
│  ├──pico_crypto_key
│  │  ├──build.py
│  │  ├──device.py
│  │  └──__init__.py
│  ├──pico-sdk -> ../pico-sdk-1.5.1
│  ├──pyproject.toml
│  ├──README.md
│  ├──src
│  └──test
├──pico-sdk-1.5.1
│  └──lib
│     ├──cyw43-driver -> ../../cyw43-driver-1.0.3 *
│     └──tinyusb -> ../../tinyusb-0.16.0
└──tinyusb-0.16.0

* required for pico_w only
```

## Configure

If using a fresh download of `mbedtls` - run the configuration script to customise the build for the Pico, e.g.:

```sh
./configure-mbedtls.sh
```

More info [here](https://tls.mbed.org/discussions/generic/mbedtls-build-for-arm)

## Build

If using a Pico W you can use the additional option `--board pico_w` when running `check`, `build`, `install` or `reset-pin`. This will ensure the LED will work. (Images built for the Pico will work on a Pico W aside from the LED.)

These steps use the `picobuild` script. (See `picobuild --help`.) Optionally check your configuration looks correct then build:

```sh
picobuild check
picobuild build
```

Ensure your device is connected and mounted ready to accept a new image (press `BOOTSEL` when connecting), then:

```sh
picobuild install /path/to/RPI-RP2
picobuild test
```

## PIN protection

The device is protected with a PIN, the salted hash of which is read from flash memory. Before first use (or a forgotten PIN), a hash must be written to flash (press `BOOTSEL` when connecting):

```sh
picobuild reset-pin /path/to/RPI-RP2
```

If the device LED is flashing after this, the reset failed - the flash memory may be worn. Otherwise now reinstall the crypto key image as above. The pin will then be "pico", and it can be changed - see the [example](#change-pin).

The python driver will first check for an env var `PICO_CRYPTO_KEY_PIN` and fall back to a prompt if this is not present.

(NB for the tests to run, the env var *must* be set)

## Using the device

The `CryptoKey` class provides the python interface and is context-managed to help ensure the device gets properly opened and closed. The correct pin must be provided to activate it. Methods available are:

- `pubkey` return the ECDSA public key (short-form, 33 bytes)
- `hash` compute the SHA256 hash of the input
- `sign` compute the SHA256 hash and ECDSA signature of the input
- `verify` verify the given hash matches the signature and public key
- `encrypt` encrypts using AES256
- `decrypt` decrypts using AES256
- `register` dynamically create an ECDSA public key for verifying, along the lines of WebAuthn
- `auth` generates a one-time ECDSA-based authentication string, along the lines of WebAuthn
- `set_pin` set a new PIN
- `info` returns version, board type and device time

See the examples for more details.

## Errors

The device LED is normally off when the device is idle, and on when it's doing something. If there are low-level errors with any of the crypto algorithms then the device may enter an unrecoverable error state where the LED will flash. The error codes can be interpreted like so:

Long flashes | Short flashes | Algorithm | mbedtls error code
------------:|--------------:|-----------|-------------------
1            | 0             | ECDSA     | Unknown error
1            | 1             | ECDSA     | `MBEDTLS_ERR_ECP_BAD_INPUT_DATA`
1            | 2             | ECDSA     | `MBEDTLS_ERR_ECP_BUFFER_TOO_SMALL`
1            | 3             | ECDSA     | `MBEDTLS_ERR_ECP_FEATURE_UNAVAILABLE`
1            | 4             | ECDSA     | `MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED`
1            | 5             | ECDSA     | `MBEDTLS_ERR_MPI_ALLOC_FAILED`
2            | 0             | AES       | Unknown error
2            | 1             | AES       | `MBEDTLS_ERR_AES_INVALID_KEY_LENGTH`
3            | 0             | SHA       | Unknown error


## Troubleshooting

- If you get `[Errno 13] Permission denied: '/dev/ttyACM0'`, adding yourself to the `dialout` group and rebooting should fix.
- If you get `usb.core.USBError: [Errno 13] Access denied (insufficient permissions)` you'll need to add a udev rule for the device, see [this stackoverflow post](https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the). This worked for me:

  `SUBSYSTEMS=="usb", ENV{DEVTYPE}=="usb_device", ATTRS{idVendor}=="aafe", ATTRS{idProduct}=="c0ff", GROUP="plugdev", MODE="0777"`

- the device can get out of sync quite easily when something goes wrong. If so, turn it off and on again ;)

## Examples

### Hash file

This script just prints the hash of itself.

```sh
$ python examples/hash_file.py examples/hash_file.py
PicoCryptoKey 1.3.0-pico
examples/hash_file.py: f99e202cdb1c7091f291a3361eac6b8d2230eef28bd165415e86ec235b03a938
```

### Encrypt/decrypt data

This example will look for an encrypted version of the data (examples/dataframe.csv). If not found it will first encrypt the plaintext.

Then it decrypts the ciphertext and loads the data into a pandas dataframe (you may need to install pandas).

```sh
python examples/decrypt_data.py
```

If you are using the same device you used to encrypt the data, you should see something like this:

```text
decryption took 2.56s
           Area  DC1117EW_C_SEX  DC1117EW_C_AGE NewEthpop_ETH
0     E02001730               2              62           WBI
1     E02001713               2              60           WBI
2     E02001713               1              30           WBI
3     E02001736               1              41           OAS
4     E02001719               2              22           WBI
...         ...             ...             ...           ...
5630  E02001721               1              60           WBI
5631  E02001720               1              22           WBI
5632  E02001729               2              24           MIX
5633  E02006893               1              32           WBI
5634  E02001708               1              28           OAS

[5635 rows x 4 columns]
```

If you now switch to a different device, it won't be able to decrypt the ciphertext and will return garbage.

### Sign data

This example will compute a hash (SHA256) of a file and sign it. It outputs a json object containing the filename, the hash, the signature, and the device's public key.

```sh
python examples/sign_data.py
```

gives you something like

```text
PicoCryptoKey 1.3.0-pico
signing took 0.46s
signature written to signature.json
```

where signature.json contains

```json
{
  "file": "examples/dataframe.csv",
  "hash": "28d839df69762085f8ac7b360cd5ee0435030247143260cfaff0b313f99a251c",
  "signature": "30460221009531919bd13f964544fb494393e1bea1cf5a04a53d572e914ea1cbc30657166c022100e1d1394240eb9a8269eafa8d06a82d1c087a0af260576577da5f45352ebb4162",
  "pubkey": "020a7dfbd2272ad9e9d49dd11aec4743d10ba3d9e3affc3fa3a64c8a28fd78a212"
}
```

### Verify data

The signature data above should be verifiable by any ECDSA validation algorithm, but you can use the device for this. First it verifies the supplied hash corresponds to the file, then it verifies the signature against the hash and the given public key. It also prints whether the public key provided matches it's own public key.

```sh
python examples/verify_data.py
```

```text
PicoCryptoKey 1.3.0-pico
file hash matches file
verifying device is the signing device
signature is valid
verifying took 0.79s
```

or, if you use a different board

```text
PicoCryptoKey 1.3.0-pico
file hash matches file
verifying device is not the signing device
signature is valid
verifying took 0.79s
```

### Authenticate

Step 1 generates registration keys for two receiving parties - these are short-form ECDSA public keys.

Step 2 generates a time-based auth tokens for each receiving party from a challenge string. The tokens are base64-encoded ECDSA signatures of the SHA256 of the challenge appended with the timestamp rounded to the minute.

Third-party code (the ecdsa python package) is then used to verify the public key-auth token pairs.

```sh
python examples/auth.py
```

```txt
PicoCryptoKey 1.3.0-pico 2024-05-06 09:01:39.648000+00:00
Host-device time diff: 0.001054s
registered example.com: 02fb8816ea34387378179d046f814ec8efaa122f4bc84ad268880bcb9a2e44f6f9
registered another.org: 02614fa67aa3600af7a69031cb1d69f05a8c8fdf32d1ee9db7cee24a6c172b6998
challenge is: b'testing time-based auth'
auth response example.com: b'MEYCIQD3QnVHSaq9x72PYL0HK/6+VNXBKnoe+zMiHS7nekae7AIhAPbWWIukcuvbe035Y7l00ErsSh5gjs7dgozbGcsAxRmH'
auth response another.org: b'MEYCIQDYROjJcsM261ogYPPG8RR8G0QETr5DiKxgJWPQsycveAIhANc6R8YVYpqZlPSwkeihaJWl/YLxCuRbzeMk9XRqs82/'
example.com verified: True
another.org verified: True
example.com cannot verify b'MEYCIQDYROjJcsM261ogYPPG8RR8G0QETr5DiKxgJWPQsycveAIhANc6R8YVYpqZlPSwkeihaJWl/YLxCuRbzeMk9XRqs82/'
another.org cannot verify b'MEYCIQD3QnVHSaq9x72PYL0HK/6+VNXBKnoe+zMiHS7nekae7AIhAPbWWIukcuvbe035Y7l00ErsSh5gjs7dgozbGcsAxRmH'```
```

### Authenticate (client-server)

As above, but using a webauthn-style workflow using a local python script as a proxy for a client (would normally be a website), connecting to the crypto key via a (local) socket to a server script connected to the crypto key.

First run

```sh
$ python examples/webauthn_server.py
PIN:****
2024-05-27 22:05:41 INFO     1.3.0-pico @ 2024-05-27 21:05:41.165000+00:00
2024-05-27 22:05:41 INFO     listening for requests on localhost:5000
```

Then the client script will register and auth, like in the example above:

```sh
$ python webauthn_client.py
registered example.com: 02fb8816ea34387378179d046f814ec8efaa122f4bc84ad268880bcb9a2e44f6f9
challenge is: b'auth me now!'
auth response example.com: MEUCIQDftDi2LfYY8FMVP8d4gjVMJpyYArwWV1rYjWaMqaVrlQIgazKzgYjWxaFuCzpXdI3hByb3zn+k5xjZ47TqFHAZLFc=
example.com verified: True
```

Meanwhile, the server says:

```sh
...
2024-05-27 22:05:46 INFO     127.0.0.1 requests register:{'host': 'example.com'}
2024-05-27 22:05:46 INFO     registering with example.com: 02fb8816ea34387378179d046f814ec8efaa122f4bc84ad268880bcb9a2e44f6f9
2024-05-27 22:05:46 INFO     127.0.0.1 requests auth:{'host': 'example.com', 'challenge': 'auth me now!'}
2024-05-27 22:05:46 INFO     Host-device time diff: 0.001346s
2024-05-27 22:05:46 INFO     authing with example.com challenge=auth me now! response=b'MEUCIQCk5o1n5CijdYFPiaGxFV0SfLRb5S8xdzUnZ1cIALYiLAIge7s8yBgjtEPPyV//3CbcUVRYj+fCi0ipqbfFurrVAv4='
```

### Change PIN

```sh
python examples/change_pin.py
```

This just runs the PIN reset process:

- initialise device
- reset device (you'll need to enter the old PIN, even if this was set in the env)
- enter new PIN and repeat to confirm
- write new PIN to device
- reset device and initialise with new PIN

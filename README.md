# pico-crypto-key

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/fb9853538e3a421d9715812f87f3269d)](https://www.codacy.com/gh/virgesmith/pico-crypto-key/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virgesmith/pico-crypto-key&amp;utm_campaign=Badge_Grade)

Using a Raspberry Pi [pico](https://www.raspberrypi.org/products/raspberry-pi-pico/) microcontroller as a USB security device that provides:

- cryptographic hashing (SHA256)
- encryption and decryption (256 bit AES)
- cryptographic signing and verification (256 bit ECDSA - secp256k1, as Bitcoin)

I'm not a security expert and the device/software is almost certainly not hardened enough for serious use. I just did it cos it was there, and I was bored. Also, it's not fast, but that might be ok depending on your current lockdown status. Most importantly, it works. Here's some steps I took towards making it securer:

- the device is pin protected. Only the sha256 hash of the (salted) pin is stored on the device.
- the private key is only initialised once a correct pin has been entered, and is a sha256 hash of the (salted) unique device id of the pico. So no two devices should have the same key.
- the private key never leaves the device and is stored only in volatile memory.

## Dependencies/prerequisites

`pico-crypto-key` comes as a python (dev) package that provides:

- a simplified build process
- a python interface to the device.

First, clone/fork this repo and install the package in development (editable) mode:

```sh
pip install -e .
```

If this step fails, try upgrading to a more recent version of pip.

The project file [pyproject.toml](./pyproject.toml) reflects the current hardware library versions. Change as necessary.

- Toolchain (arm cross-compiler) and [pico-sdk](https://github.com/raspberrypi/pico-sdk): See [here](https://www.raspberrypi.org/documentation/pico/getting-started/) for more info on getting set up if necessary, and download and extract a release, e.g. [1.4.0](hhttps://github.com/raspberrypi/pico-sdk/archive/refs/tags/1.4.0.tar.gz)

- Download and extract [tinyusb](https://github.com/hathach/tinyusb/releases/tag/0.13.0). Replace the empty `pico-sdk-1.4.0/lib/tinyusb` directory with a symlink to where you extracted it, e.g.

  ```sh
  cd pico-sdk-1.4.0/lib
  rmdir tinyusb
  ln -s ../../tinyusb-0.13.0 tinyusb
  ```

- [mbedtls](https://tls.mbed.org/api/): see also the [code](https://github.com/ARMmbed/mbedtls). Currently using the 3.2.1 release/tag. Download a release of mbedtls, and symlink to to `mbedtls` in the project root, e.g.

- Create symlinks in the project root to the pico SDK and mbedtls, e.g.:

```sh
ln -s ../pico-sdk-1.4.0 pico-sdk
ln -s ../mbedtls-3.2.1 mbedtls
```

You should end up with a structure something like this:

```sh
.
├── mbedtls-3.2.1
├── pico-crypto-key
│   ├── examples
│   ├── mbedtls -> ../mbedtls-3.2.1
│   ├── pico_crypto_key
│   │   ├── build.py
│   │   ├── device.py
│   │   └── __init__.py
│   ├── pico-sdk -> ../pico-sdk-1.4.0
│   ├── pico_sdk_import.cmake
│   ├── pyproject.toml
│   ├── README.md
│   ├── setup.cfg
│   ├── src
│   └── test
├── pico-sdk-1.4.0
│   └── lib
│       └── tinyusb -> ../../tinyusb-0.13.0
└── tinyusb-0.13.0
```

### Configure

If using a fresh download of `mbedtls` - run the configuration script to customise the build for the pico, e.g.:

```sh
./configure-mbedtls.sh
```

More info [here](https://tls.mbed.org/discussions/generic/mbedtls-build-for-arm)

## Build

Use the `picobuild` script. E.g. to clean, rebuild, install and test:

```sh
picobuild clean
picobuild build
```

Ensure your device is connected and ready to accept a new image (press BOOTSEL when connecting), then:

```
picobuild install /media/username/RPI-RP2
picobuild test
```

(The default device path and the device PIN are currently defined in [pyproject.toml](./pyproject.toml))

## Using the device

The device is pin protected (the word 'pico'), and (for now) it can't be changed. Sending the correct pin to the device activates the repl (read-evaluate-print loop).

Both the tests and examples read the serial port and the pin from the `[pico.run]` section in [pyproject.toml](./pyproject.toml). Modify the settings as necessary.

The python interface (the `CryptoKey` class) is context-managed to help ensure the device gets properly opened and closed.

### Troubleshooting

- If you get `[Errno 13] Permission denied: '/dev/ttyACM0'`, adding yourself to the `dialout` group and rebooting should fix.

- the device can get out of sync quite (too) easily. If so, turn it off and on again ;)

### Testing

Just run:

```sh
pytest
```

## Examples

The examples use small (<100kB) files, as device communication is currently only ~100kb/s.

### 0. Get device help

This just prints the device's help.

```sh
python examples/device_help.py
```

```text
The device must first be supplied with a correct pin to enter the repl
repl commands:
H displays this message
h computes sha256 hash of data streamed to device
  inputs: <data> <data> <data>... <>
  returns: <hash>
k get the public key
  inputs: none
  returns: <pubkey>
d decrypts each chunk of streamed data
  inputs: <data> <data>... <>
  returns: <data> <data>...
e encrypts each chunk of streamed data
  inputs: <data> <data>... <>
  returns: <data> <data>...
s hashes and signs (the hash of) the streamed data
  inputs: <data> <data>... <>
  returns: <hash> <sig>
v verifies a signature
  inputs: <hash> <sig> <pubkey>
  returns: stringified integer. 0 if verification was successful
r resets the device repl (i.e. pin will need to be reentered)
  inputs: none
  returns: nothing
All commands are a single character (no newline).
All data sent and received is base64 encoded and terminated with a newline,
unless otherwise specified. Where a variable number of inputs is received,
a blank line is used to indicate the end of the data.
```

### 1. Encrypt data

This example will look for an encrypted version of the data. If not found it will encrypt the plaintext. Then it decrypts the ciphertext and loads the data into a pandas dataframe (you may need to install pandas).

```sh
python examples/encrypt_df.py
```

You should see something like this:

```text
decryption took 6.48s
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

If you now switch to a different device, the decryption will return garbage, and you'll get something like this:

```text
invalid data: 'utf-8' codec can't decode byte 0xf4 in position 0: invalid continuation byte
decryption took 7.04s
None
```

### 3. Sign data

This example will compute a hash (SHA256) of a file and sign it. It outputs a json object containing the filename, the hash, the signature, and the device's public key.

```sh
python examples/sign_data.py
```

gives you something like

```text
signing/verifying took 4.44s
{
  "file": "./examples/dataframe.csv",
  "hash": "28d839df69762085f8ac7b360cd5ee0435030247143260cfaff0b313f99a251c",
  "sig": "304602210089d4bc103d00e2e23f0a911444b2a472a7950c74dbf69c3e2f0268b1207ca248022100fe38989e486cf2a2a8c13844d8a1647674b3d641ee4d29a73e8138db31c9ed90",
  "pubkey": "0486bb625d67b45d82c7b3cc087984abea8d4acc5d1fb70691387594f167929892e147364318d4ce2d2eefec134fa1d531a7e7b2421d945bb563bd4d115aeb7178"
}
```

### 3. Verify data

The signature data above should be verifiable by any ECDSA validation algorithm, but you can use the device for this. First it verifies the supplied hash corresponds to the file, then it verifies the signature against the hash and the given public key. It also prints whether the public key provided matches it's own public key.

```sh
python examples/verify_data.py
```

```text
verifying device is the same as signing device
hashing/verifying took 4.40s
verified: True
```

or, if you use a different pico

```text
verifying device is NOT the signing device (which is good)
hashing/verifying took 4.46s
verified: True
```

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

First, clone/fork this repo and run

```sh
pip install -e .
```

The file [config.toml](./config.toml) reflects the current hardware library versions. Change as necessary.

- [pico-sdk](https://github.com/raspberrypi/pico-sdk): See [here](https://www.raspberrypi.org/documentation/pico/getting-started/) for more info on getting set up if necessary, and download and extract a release, e.g. [1.3.0](hhttps://github.com/raspberrypi/pico-sdk/archive/refs/tags/1.3.0.tar.gz)

- Download and extract [tinyusb](https://github.com/hathach/tinyusb/releases/tag/0.13.0). Replace the empty `pico-sdk-1.3.0/lib/tinyusb` directory with a symlink to where you extracted it, e.g.

  ```sh
  cd pico-sdk-1.3.0/lib
  rmdir tinyusb
  ln -s ../../tinyusb-0.13.0 tinyusb
  ```

- [mbedtls](https://tls.mbed.org/api/): see also the [code](https://github.com/ARMmbed/mbedtls). Currently using the 2.28.0 release/tag. Download a release of mbedtls and extract in the project root (so you have a subdir like `mbedtls-2.28.0`). You will need to edit [CMakeLists.txt](./CMakeLists.txt) if you change this.

### Configure

If using a fresh download of `mbedtls` - in that subdirectory, use their python script to configure the build:

```sh
scripts/config.py unset MBEDTLS_NET_C
scripts/config.py unset MBEDTLS_TIMING_C
scripts/config.py unset MBEDTLS_FS_IO
scripts/config.py unset MBEDTLS_PSA_ITS_FILE_C
scripts/config.py set MBEDTLS_NO_PLATFORM_ENTROPY
scripts/config.py unset MBEDTLS_PSA_CRYPTO_C
scripts/config.py unset MBEDTLS_PSA_CRYPTO_STORAGE_C
```

More info [here](https://tls.mbed.org/discussions/generic/mbedtls-build-for-arm)

## Build

### Automated

Ensure settings in `config.toml` are correct, and your device is connected and ready to accept a new image, then

```sh
python pico_crypto_key/build.py
```

### Manual (legacy)

Copy `pico_sdk_import.cmake` from the `external` subdir of the pico SDK to your project root. Ensure `PICO_SDK_PATH` env var is set correctly, then from the project root,

```sh
mkdir build && cd build && cmake ..
```

then

```sh
make -j
```

Now copy `crypto.uf2` to your pico device (see pico documentation for more detail).

## Test

Tests use pytest, just do:

```sh
pytest
```

The tests use the [config.toml](./config.toml) to locate the device (typically `/dev/ttyACM0`), adjust as necessary. If you get `[Errno 13] Permission denied: '/dev/ttyACM0'`, adding yourself to the `dialout` group and rebooting should fix.

The device is pin protected (the word 'pico'), and (for now) it can't be changed. Sending the correct pin to the device activates the repl (read-evaluate-print loop). The host-side python wrapper gets the pin from the `PICO_CRYPTO_KEY_PIN` entry in [config.toml](./config.toml).

NB the device can get out of sync quite easily. If so, turn it off and on again ;)

## Examples

The examples use small (<100kB) files, as device communication is currently only ~100kb/s.

### 0. Get device help

This just prints the device's help.

```sh
python examples/device_help.py
```

### 1. Encrypt data

This example will look for an encrypted version of the data. If not found it will encrypt the plaintext. Then it decrypts the ciphertext and loads the data into a pandas dataframe.

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

# crypto-key

Using a raspberry pi pico microcontroller as a USB security device that provides:

- cryptographic hashing (SHA256)
- encryption and decryption (256 bit AES)
- cryptographic signature and verification (256 bit ECDSA)

I'm not a security expert and the device/software is almost certainly not hardened enough for serious use. I just did it cos it was there, and I was bored.

## dependencies

Clone the [pico-sdk](https://github.com/raspberrypi/pico-sdk). I'm currently using the master branch.

See [here](https://www.raspberrypi.org/documentation/pico/getting-started/) for more info on getting set up if necessary.

[mbedtls documentation](https://tls.mbed.org/api/) and [mbedtls code](https://github.com/ARMmbed/mbedtls). I used the 2.25.0 release/tag.

Unzip mbedtls as a subdirectory of the project root.

### configure

In the mbedtls directory, use their python script to configure the build.

```bash
scripts/config.py unset MBEDTLS_NET_C
scripts/config.py unset MBEDTLS_TIMING_C
scripts/config.py unset MBEDTLS_FS_IO
scripts/config.py unset MBEDTLS_PSA_ITS_FILE_C
scripts/config.py set MBEDTLS_NO_PLATFORM_ENTROPY
scripts/config.py unset MBEDTLS_PSA_CRYPTO_C
```
More info [here](https://tls.mbed.org/discussions/generic/mbedtls-build-for-arm)

## build

Back in te project root,

```bash
mkdir build && cd build && cmake ..
```

then

```bash
make -j4
```

## test

```bash
PYTHONPATH=. python test/run.py
```

(`PYTHONPATH` is required whilst crypto_device is not packaged)

### use-cases

```bash
PYTHONPATH=. python use-cases/run.py
```

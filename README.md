# pico-crypto-key

Using a Raspberry Pi [pico](https://www.raspberrypi.org/products/raspberry-pi-pico/) microcontroller as a USB security device that provides:

- cryptographic hashing (SHA256)
- encryption and decryption (256 bit AES)
- cryptographic signing and verification (256 bit ECDSA)

I'm not a security expert and the device/software is almost certainly not hardened enough for serious use. I just did it cos it was there, and I was bored. Also, it's not fast, but that might be ok depending on your current lockdown status. Most importantly, it works.

The private key is based on the unique device id of the pico, so no two devices should have the same key.

## dependencies

Clone the [pico-sdk](https://github.com/raspberrypi/pico-sdk). I'm currently using the master branch.

See [here](https://www.raspberrypi.org/documentation/pico/getting-started/) for more info on getting set up if necessary.

See also the [mbedtls documentation](https://tls.mbed.org/api/) and [mbedtls code](https://github.com/ARMmbed/mbedtls). I used the 2.25.0 release/tag.

Download a release of mbedtls and extract in the project root (so you have a subdir like `mbedtls-2.25.0`).

### configure

In the mbedtls subdirectory, use their python script to configure the build.

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

Now copy `crypto.uf2` to your pico device (see pico documentation for more detail).

## test

Tests assume the device is located at `/dev/ttyACM0`, adjust the code as necessary.

```bash
PYTHONPATH=. python test/run.py
```

(`PYTHONPATH` is required whilst `crypto_device.py` is not packaged)

## use cases

The use cases use a small (~100kB) csv file.

### 1. encrypt data

This example will look for an encrypted version of the data. If not found it will encrypt the plaintext. Then it decrypts the ciphertext and loads the data into a pandas dataframe.

```bash
PYTHONPATH=. python use-cases/encrypted_df.py
```

You should see something like this:

```text
decryption took 9.16s
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
closing serial connection
```

If you now switch to a different device, the decryption will return garbage, and you'll get something like this:

```text
invalid data: 'utf-8' codec can't decode byte 0xf4 in position 0: invalid continuation byte
decryption took 9.04s
None
closing serial connection
```

### 2. sign data

```bash
PYTHONPATH=. python use-cases/sign_data.py
```
gives you something like

```text
signing/verifying took 6.95s
{
  "file": "./use-cases/dataframe.csv",
  "hash": "28d839df69762085f8ac7b360cd5ee0435030247143260cfaff0b313f99a251c",
  "sig": "304602210089d4bc103d00e2e23f0a911444b2a472a7950c74dbf69c3e2f0268b1207ca248022100fe38989e486cf2a2a8c13844d8a1647674b3d641ee4d29a73e8138db31c9ed90",
  "pubkey": "0486bb625d67b45d82c7b3cc087984abea8d4acc5d1fb70691387594f167929892e147364318d4ce2d2eefec134fa1d531a7e7b2421d945bb563bd4d115aeb7178"
}
closing serial connection
```

### 3. verify data

The signature data above should be verifiable by any ECDSA validation algorithm, but you can use the device for this. First it verifies the supplied hash corresponds to the file, then it verifies the signature against the hash and the given public key.

```bash
PYTHONPATH=. python use-cases/verify_data.py
```

```text
verifying device is the same as signing device
hashing/verifying took 7.11s
verified: True
closing serial connection
```

or, if you use a different pico

```
verifying device is NOT the signing device (which is good)
hashing/verifying took 6.86s
verified: True
closing serial connection
```
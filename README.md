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

## Update v1.1.0

The device now uses USB CDC rather than serial to communicate with the host which allows much faster bitrates and avoids the need to encode binary data. Performance is improved, but varies considerably by task (results are for a 1000k input):

| task    | CDC<br>time(s) | CDC<br>bitrate(kbps) | serial<br>time(s) | serial<br>bitrate(kbps)| Speedup(%) |
|:--------|---------------:|---------------------:|------------------:|-----------------------:|-----------:|
| hash    |            2.6 |               3026.3 |              19.6 |                  407.9 |      641.9 |
| sign    |            2.8 |               2904.1 |              19.6 |                  408.3 |      611.3 |
| verify  |            0.4 |                      |               0.5 |                        |       16.0 |
| encrypt |           23.9 |                334.2 |              43.5 |                  183.8 |       81.9 |
| decrypt |           23.8 |                336.0 |              43.1 |                  185.7 |       81.0 |



## Dependencies/prerequisites

`pico-crypto-key` comes as a python (dev) package that provides:

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

- download [mbedtls](https://tls.mbed.org/api/): see also their [repo](https://github.com/ARMmbed/mbedtls). Currently using the 3.6.0 release/tag.

- create symlinks in the project root to the pico SDK and mbedtls, e.g.:

  ```sh
  ln -s ../pico-sdk-1.5.1 pico-sdk
  ln -s ../mbedtls-3.6.0 mbedtls
  ```

You should now have a structure something like this:

```txt
.
├── mbedtls-3.6.0
├── pico-crypto-key
│   ├── examples
│   ├── mbedtls -> ../mbedtls-3.6.0
│   ├── pico_crypto_key
│   │   ├── build.py
│   │   ├── device.py
│   │   └── __init__.py
│   ├── pico-sdk -> ../pico-sdk-1.5.1
│   ├── pyproject.toml
│   ├── README.md
│   ├── setup.cfg
│   ├── src
│   └── test
├── pico-sdk-1.5.1
│   └── lib
│       └── tinyusb -> ../../tinyusb-0.16.0
└── tinyusb-0.16.0
```

### Configure

If using a fresh download of `mbedtls` - run the configuration script to customise the build for the pico, e.g.:

```sh
./configure-mbedtls.sh
```

More info [here](https://tls.mbed.org/discussions/generic/mbedtls-build-for-arm)

## Build

These steps use the `picobuild` script. Optionally check your configuration looks correct then build:

```sh
picobuild check
picobuild build
```

Ensure your device is connected and mounted ready to accept a new image (press BOOTSEL when connecting), then:

```sh
picobuild install /path/to/RPI-RP2
picobuild test
```

## PIN protection

The device is protected with a PIN, the salted hash of which is read from flash memory. Before first use (or a forgotten PIN), a hash must be written to flash (press BOOTSEL when connecting):

```sh
picobuild reset-pin /path/to/RPI-RP2
```

then reinstall the crypto key image as above. The pin will then be "pico", and it can be changed (see below).

The python interface will first check for an env var `PICO_CRYPTO_KEY_PIN` and fall back to a prompt if this is not present.

(NB for the tests to run, the env var *must* be set)

## Using the device

The device is pin protected (default is the word 'pico')

The `CryptoKey` class provides the python interface and is context-managed to help ensure the device gets properly opened and closed. The correct pin must be provided to activate it.

- `pubkey` return the ECDSA public key (long-form, 65 bytes)
- `hash` compute the SHA256 hash of the input
- `sign` compute the SHA256 hash and ECDSA signature of the input
- `verify` verify the given hash matches the signature and public key
- `encrypt` encrypts using AES256
- `decrypt` decrypts using AES256
- `set_pin` set a new PIN

See the examples for more details.


### Troubleshooting

- If you get `[Errno 13] Permission denied: '/dev/ttyACM0'`, adding yourself to the `dialout` group and rebooting should fix.
- If you get `usb.core.USBError: [Errno 13] Access denied (insufficient permissions)` you'll need to add a udev rule for the device, see [this stackoverflow post](https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the). This worked for me:

  `SUBSYSTEMS=="usb", ENV{DEVTYPE}=="usb_device", ATTRS{idVendor}=="aafe", ATTRS{idProduct}=="c0ff", GROUP="plugdev", MODE="0777"`


- the device can get out of sync quite easily when something goes wrong. If so, turn it off and on again ;)


## Examples

### Hash file

This just prints the hash of itself.

```sh
python examples/hash_file.py
```

### Encrypt/decrypt data

This example will look for an encrypted version of the data (examples/dataframe.csv). If not found it will encrypt the plaintext.

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
signing/verifying took 0.55s
signature written to signature.json
```

### Verify data

The signature data above should be verifiable by any ECDSA validation algorithm, but you can use the device for this. First it verifies the supplied hash corresponds to the file, then it verifies the signature against the hash and the given public key. It also prints whether the public key provided matches it's own public key.

```sh
python examples/verify_data.py
```

```text
file hash matches file
verifying device is the signing device
signature is valid
verifying took 0.79s
```

or, if you use a different pico

```text
file hash matches file
verifying device is not the signing device
signature is valid
verifying took 0.79s
```

### Change PIN

This just runs the PIN reset process:
- initialise device
- reset device (you may need to enter the old PIN again)
- enter new PIN and repeat to confirm
- write new PIN to device
- reset device and initialise with new PIN
# pico-crypto-key

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/fb9853538e3a421d9715812f87f3269d)](https://www.codacy.com/gh/virgesmith/pico-crypto-key/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virgesmith/pico-crypto-key&amp;utm_campaign=Badge_Grade)

Using Raspberry Pi RP2040/RP2350 microcontrollers as USB security devices that provide:

- cryptographic hashing (SHA256)
- encryption and decryption (256 bit AES)
- public key cryptography (ECDSA - secp256k1, as Bitcoin)

I'm not a security expert and the device/software is almost certainly not hardened enough for serious use (perhaps RP2350 ARM-secure will fix that?). I just did it cos it was there, and I was bored. Also, it's not fast, but that might be ok depending on your current lockdown status. Most importantly, it works. Here's some steps I took towards making it securer:

- the device is pin protected. Only the SHA256 hash of the (salted) pin is stored on the device.
- the private key is only initialised once a correct pin has been entered, and is a SHA256 hash of the (salted) unique device id. So no two devices should have the same key.
- the private key never leaves the device and is stored only in volatile memory.

Pico, Pico W, Tiny2040, Pico2 and Pico2 W boards are known to work. Other RP2040/RP2350 boards have not been tested but are likely to (mostly) work. E.g. the Pico/Pico2 W requires the wifi driver purely for the LED (which is connected to the wifi chip) to function (though neither wifi nor bluetooth are enabled.)

## Notes/issues

- This project uses MbedTLS 3, which is not supported by the SDK (which still uses MbedTLS 2), so must be kept separate.
- Writes to the final flash block do not persist on RP2350. See [here](https://forums.raspberrypi.com/viewtopic.php?t=375912). Simple workaround is to use the penultimate block.
- Some prebuilt RISC-V toolchains do not work, see [here](https://forums.raspberrypi.com/viewtopic.php?t=375713). Using
the binaries available at [pico-sdk-tools](https://github.com/raspberrypi/pico-sdk-tools/releases/) is recommended.

## Performance

### RP2040 vs RP2350 ARM vs RP2350 RISC-V

v1.4.0 introduced support for RP2350 boards. Performance improvement is fairly modest, Cortex M33 slightly outperforming the Hazard3 - but the bottleneck here is USB comms. Note that using hardware SHA256 only seems to improve hashing performance by about 6% for this (IO-bound) use case.

|         | RP2040<br/>time(s) | <br/>bitrate(kbps) | RP2350(ARM)<br/>time(s) | <br/>bitrate(kbps) | <br/>speedup(%) | RP2350(RISC-V)<br/>time(s) | <br/>bitrate(kbps) | <br/>speedup(%) |
|:--------|-------------------:|-------------------:|------------------------:|-------------------:|----------------:|---------------------------:|-------------------:|----------------:|
| hash    |                2.6 |             3099.2 |                     1.8 |             4557.3 |            47.0 |                        1.8 |             4503.0 |            45.3 |
| sign    |                2.7 |             2996.8 |                     1.9 |             4239.9 |            41.5 |                        1.8 |             4384.3 |            46.3 |
| verify  |                0.5 |                    |                     0.2 |                    |           117.6 |                        0.3 |                    |            81.0 |
| encrypt |               23.8 |              335.8 |                    11.2 |              713.5 |           112.5 |                       13.2 |              604.5 |            80.0 |
| decrypt |               23.8 |              336.6 |                    11.2 |              714.5 |           112.3 |                       13.2 |              604.3 |            79.5 |

Tests run on a single core and use a 1000kB random binary data input. Binaries compiled with 10.3.1 ARM and 14.2.1 RISC-V gcc toolchains.

On thing not measured or considered here is the difference in power consumption between Cortex M33 vs Hazard3...


### USB speed

v1.1.0 switched to USB CDC rather than serial to communicate with the host which allows much faster bitrates and avoids the need to encode binary data. Performance is improved, but varies considerably by task (results are for a 1000kB input on a RP2040):

| task    | CDC<br>time(s) | CDC<br>bitrate(kbps) | serial<br>time(s) | serial<br>bitrate(kbps)| Speedup(%) |
|:--------|---------------:|---------------------:|------------------:|-----------------------:|-----------:|
| hash    |            2.6 |               3026.3 |              19.6 |                  407.9 |      641.9 |
| sign    |            2.8 |               2904.1 |              19.6 |                  408.3 |      611.3 |
| verify  |            0.4 |                      |               0.5 |                        |       16.0 |
| encrypt |           23.9 |                334.2 |              43.5 |                  183.8 |       81.9 |
| decrypt |           23.8 |                336.0 |              43.1 |                  185.7 |       81.0 |


## Usage

`pico-crypto-key` is a python (dev) package that provides:

- a simplified build process supporting multiple configurations
- a python interface to the devices.

### Dependencies/prerequisites

First, clone/fork this repo and install the package in development (editable) mode:

```sh
pip install --group dev -e .
```

or

```sh
uv sync --group dev
```

If this step fails, try upgrading to a more recent version of pip.

You will then need to:

- install the compiler toolchain(s) and cmake:

  ```sh
  sudo apt install gcc-arm-none-eabi cmake
  ```

  For RISC-V, prebuilt toolchains can be found [here](https://github.com/raspberrypi/pico-sdk-tools/releases).

- clone [pico-sdk](https://github.com/raspberrypi/pico-sdk) see [here](https://www.raspberrypi.org/documentation/pico/getting-started/). Initialise submodules:

  ```sh
  git submodule update --init
  ```

- since SDK v2.0.0, you will also need to build and install [picotool](https://github.com/raspberrypi/picotool) corresponding to the SDK version you're using.

- download a release of [mbedtls](https://tls.mbed.org/api/) - the `.tar.bz2` asset. Currently using the 3.6.2 release/tag. **This is a different version to the one in the SDK** (which still uses v2) so must be kept separate. It also requires a custom configuration. Create a symlink in the project root to mbedtls, e.g.:

  ```sh
  ln -s ../mbedtls-3.6.2 mbedtls
  ```

## Configure

In the `config/boards.toml` file ensure settings for `PICO_TOOLCHAIN_PATH` and `PICO_SDK_PATH` are correct.

If using a fresh download of `mbedtls` - run the configuration script to customise the build for the Pico, e.g.:

```sh
./configure-mbedtls.sh
```

More info [here](https://tls.mbed.org/discussions/generic/mbedtls-build-for-arm)

## Supported boards

The target board must be specified using the `--board` option when running `check`, `clean`, `build`, `install` or `reset-pin`.

- Pico: `--board pico`
- Pico W: `--board pico_w`
- Pimoroni Tiny2040 2MB: `--board tiny2040`
- Pico2: `--board pico2` or `--board pico2-riscv`
- Pico2 W: `--board pico2_w` or `--board pico2_w-riscv`

Using the correct board will ensure (amongst other things?) the LED will work. (NB images built for one RP2040 board may work on other RP2040 boards, aside from the LED. YMMV...

### Board LED indicators

Board    | Init        | Ready* | Busy | Invalid | [Fatal Error](#errors)
---------|-------------|--------|------|---------|------------
Pico     | Flash       | -      | On   | -       | Flashing
Pico W   | Flash       | -      | On   | -       | Flashing
Tiny2040 | White flash | Green  | Blue | Red     | Flashing Red
Pico 2   | Flash       | -      | On   | -       | Flashing
Pico 2 W | Flash       | -      | On   | -       | Flashing

&ast; "Ready" state is only entered after a valid pin is supplied.

## Build

These steps use the `picobuild` script. (See `picobuild --help`.) Optionally check your configuration is correct then build, e.g for pico2 ARM:

```sh
picobuild check --board pico2
picobuild build --board pico2
```

Ensure your device is connected and mounted ready to accept a new image (press `BOOTSEL` when connecting), then:

```sh
picobuild install  --board pico2 /path/to/RPI-RP2
picobuild test
```

## PIN protection

The device is protected with a PIN, the salted hash of which is read from flash memory. Before first use (or a forgotten PIN), a hash must be written to flash (press `BOOTSEL` when connecting):

```sh
picobuild reset-pin /path/to/RPI-RP2
```

If the device LED is flashing (red if supported by the board) after this, the reset failed - the flash memory may be worn. Otherwise now reinstall the crypto key image as above. The pin will then be "pico", and it can be changed - see the [example](#change-pin).

The python driver will first check for an env var `PICO_CRYPTO_KEY_PIN` and fall back to a prompt if this is not present.

(NB to run the tests, either use the `--pin` command line option or set the env var)

## Using the device

On boards with multicoloured LEDs (e.g. tiny2040), initialisation is green, busy is blue and error states are red.

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

If there are low-level errors with any of the crypto algorithms then the device may enter an unrecoverable error state where the LED will flash. The error codes can be interpreted like so:

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

Step 1 generates registration keys for two relying parties - these are short-form ECDSA public keys.

Step 2 generates a time-based auth tokens for each relying party from a challenge string. The tokens are base64-encoded ECDSA signatures of the SHA256 of the challenge appended with the timestamp rounded to the minute.

Third-party code (the ecdsa python package) is then used to verify the public key-auth token pairs.

```sh
python examples/auth.py
```

```txt
PicoCryptoKey 1.3.1-pimoroni_tiny2040_2mb 2024-07-09 18:00:41.382000+00:00
Host-device time diff: 0.002865s
registered auth_user@example.com: 0334195ea7cc307c5908bd5f80b5fd0513edf5e8bf0f49c544231e089b2ea6c682
registered auth_user@another.org: 024f4f8fc6a8fca7069ffeb7122f545833ea82727fd3a8286e13f77bdbf6214dc9
challenge is: b'testing time-based auth'
auth response auth_user@example.com: b'MEQCIG4Pp5o/wXMh6RY0Z2zvr1IOBWVhQcHoRyGeQQls8genAiBaJjKeM4R4kI3DD5s3xet4R/K/bQRncyWqBoO89QILkA=='
auth response auth_user@another.org: b'MEYCIQDezWSAyNwvioDXbsO/xDMnDJLhZWWVGLhMLFNoNezRUwIhANC8gdkUtcfDcciGw9J2hbB2NdoqFP+o5RuyYQms30xk'
example.com verified: True
another.org verified: True
example.com cannot verify b'MEYCIQDezWSAyNwvioDXbsO/xDMnDJLhZWWVGLhMLFNoNezRUwIhANC8gdkUtcfDcciGw9J2hbB2NdoqFP+o5RuyYQms30xk'
another.org cannot verify b'MEQCIG4Pp5o/wXMh6RY0Z2zvr1IOBWVhQcHoRyGeQQls8genAiBaJjKeM4R4kI3DD5s3xet4R/K/bQRncyWqBoO89QILkA=='
```

### Authenticate (host-user)

As above, but using a webauthn-style workflow using a local fastapi instance (would normally be a remote website).

First start the host:

```sh
fastapi run examples/webauthn_host.py
```

When up and running, the API endpoints should be documented at [http://localhost:8000/docs](http://localhost:8000/docs)

Then use the interactive client script to interact with the crypto key and allow you to register and authenticate with the host, like in the example above:

```sh
python examples/webauthn_user.py
```

Try playing around with different users and different keys...

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

#!/bin/bash
[[ -n "$PICO_SDK_PATH" ]] || { echo "PICO_SDK_PATH not set"; exit 1; }

echo "Looking for mbedtls at $PICO_SDK_PATH/lib/mbedtls"

[[ -d "${PICO_SDK_PATH}/lib/mbedtls" ]] || { echo "mbedtls not found"; exit 1; }

cd "$PICO_SDK_PATH/lib/mbedtls"

echo Setting MBEDTLS config

scripts/config.py unset MBEDTLS_TIMING_C
scripts/config.py set MBEDTLS_NO_PLATFORM_ENTROPY
scripts/config.py unset MBEDTLS_HAVE_TIME
scripts/config.py unset MBEDTLS_HAVE_TIME_DATE

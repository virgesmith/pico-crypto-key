#!/bin/bash

# assumes there is a dir or symlink to mbedtls in the project root
cd mbedtls

scripts/config.py unset MBEDTLS_NET_C
scripts/config.py unset MBEDTLS_TIMING_C
scripts/config.py unset MBEDTLS_FS_IO
scripts/config.py unset MBEDTLS_PSA_ITS_FILE_C
scripts/config.py set MBEDTLS_NO_PLATFORM_ENTROPY
scripts/config.py unset MBEDTLS_PSA_CRYPTO_C
scripts/config.py unset MBEDTLS_PSA_CRYPTO_STORAGE_C

#!/bin/bash

# assumes there is a dir or symlink to mbedtls in the project root
cd mbedtls

# this combination of changes works for 3.5.1
scripts/config.py unset MBEDTLS_TIMING_C
scripts/config.py set MBEDTLS_NO_PLATFORM_ENTROPY
scripts/config.py unset MBEDTLS_HAVE_TIME

# plus this for 3.6.0
scripts/config.py unset MBEDTLS_HAVE_TIME_DATE

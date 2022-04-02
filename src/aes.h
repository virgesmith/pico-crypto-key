#pragma once

#include "utils.h"

#include "mbedtls/aes.h"

#include "pico/stdlib.h"

namespace aes {

const uint KEY_BITS = 256;

void key(const bytes& raw, mbedtls_aes_context& aes_key);

// decrypt stdin and output to stdout
void decrypt_stdin(const mbedtls_aes_context& key);

// encrypt stdin and output to stdout
void encrypt_stdin(const mbedtls_aes_context& key);

}
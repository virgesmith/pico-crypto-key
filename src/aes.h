#pragma once

#include "utils.h"

#include <vector>
#include <cstdint>

#include "mbedtls/aes.h"

namespace aes {

mbedtls_aes_context key(const bytes& raw);

// decrypt stdin and output to stdout
void decrypt_stdin(const mbedtls_aes_context& key);

// encrypt stdin and output to stdout
void encrypt_stdin(const mbedtls_aes_context& key);


}
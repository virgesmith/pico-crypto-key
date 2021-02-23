#pragma once

#include "utils.h"

#include <vector>
#include <cstdint>

#include "mbedtls/aes.h"
//#include "aes_bcon.h"

#define USE_MBEDTLS_AES


namespace aes {

#ifdef USE_MBEDTLS_AES
typedef mbedtls_aes_context key_t;
#else
typedef std::vector<uint32_t> key_t;
#endif

key_t key(const bytes& raw);

// decrypt stdin and output to stdout
void decrypt_stdin(const key_t& key);

// encrypt stdin and output to stdout
void encrypt_stdin(const key_t& key);


}
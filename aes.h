#pragma once

#include "utils.h"

#include <vector>
#include <cstdint>
//#include "aes_bcon.h"

namespace aes {

typedef std::vector<uint32_t> key_t;

key_t key(const bytes& raw);

// decrypt stdin and output to stdout
void decrypt_stdin(const key_t& key);

// encrypt stdin and output to stdout
void encrypt_stdin(const key_t& key);


}

#pragma once

#include "utils.h"

#include "mbedtls/ecp.h"

namespace ecdsa {

const size_t FULL_FORM_PUBKEY_LENGTH = 33;

void key(const bytes& rawkey, mbedtls_ecp_keypair& ec_key);

bytes pubkey(const mbedtls_ecp_keypair& ec_key);

bytes sign(const mbedtls_ecp_keypair& key, const bytes& hash);

// zero for success
int verify(const bytes& hash, const bytes& sig, const bytes& pubkey);

}

#pragma once

#include "utils.h"

#include "mbedtls/ecp.h"

extern "C" struct mbedtls_mpi;

namespace ecdsa {

void key(const bytes& rawkey, mbedtls_ecp_keypair& ec_key);

bytes pubkey(const mbedtls_ecp_keypair& ec_key);

bytes sign(const mbedtls_ecp_keypair& key, const bytes& hash);

// zero for success
int verify(const bytes& hash, const bytes& sig, const bytes& pubkey);

}
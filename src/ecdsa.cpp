
#include "ecdsa.h"
#include "error.h"

#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"
#include "mbedtls/pk.h"

#include "mbedtls/asn1write.h" // for local ecdsa_signature_to_asn1
#include "mbedtls/error.h"     // for local ecdsa_signature_to_asn1

#include "pico/rand.h"

#include <cstdint>
#include <cstring>

namespace {

ErrorMapper error(ErrorMapper::EC, {MBEDTLS_ERR_ECP_BAD_INPUT_DATA, MBEDTLS_ERR_ECP_BUFFER_TOO_SMALL,
                                    MBEDTLS_ERR_ECP_FEATURE_UNAVAILABLE, MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED,
                                    MBEDTLS_ERR_MPI_ALLOC_FAILED});

// copied from ecdsa.c (where its static)
int ecdsa_signature_to_asn1(const mbedtls_mpi* r, const mbedtls_mpi* s, unsigned char* sig, size_t* slen) {
  int ret = MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED;
  (void)ret; // silence lint (ret is used by the MBEDTLS_ASN1_CHK_ADD macro)
  unsigned char buf[MBEDTLS_ECDSA_MAX_LEN];
  unsigned char* p = buf + sizeof(buf);
  size_t len = 0;

  MBEDTLS_ASN1_CHK_ADD(len, mbedtls_asn1_write_mpi(&p, buf, s));
  MBEDTLS_ASN1_CHK_ADD(len, mbedtls_asn1_write_mpi(&p, buf, r));

  MBEDTLS_ASN1_CHK_ADD(len, mbedtls_asn1_write_len(&p, buf, len));
  MBEDTLS_ASN1_CHK_ADD(len, mbedtls_asn1_write_tag(&p, buf, MBEDTLS_ASN1_CONSTRUCTED | MBEDTLS_ASN1_SEQUENCE));

  memcpy(sig, p, len);
  *slen = len;

  return 0;
}

#if !defined(PICO_RAND_SEED_ENTROPY_SRC_ROSC) | !defined(PICO_RAND_ENTROPY_SRC_TIME)
#error Entropy sources not enabled
#endif

// int (*f_rng_blind)(void *, unsigned char *, size_t)
extern "C" int minstd_rand(void*, byte* p, size_t n) {
  static uint32_t r = get_rand_32();
  for (size_t i = 0; i < n; ++i) {
    r = r * 48271 % 2147483647;
    p[i] = static_cast<byte>(r); // % 256;
  }
  return 0;
}


} // namespace

void ecdsa::key(const bytes& rawkey, mbedtls_ecp_keypair& ec_key) {
  error.check(mbedtls_ecp_read_key(MBEDTLS_ECP_DP_SECP256K1, &ec_key, rawkey.data(), rawkey.size()));
  error.check(mbedtls_ecp_mul(&ec_key.grp, &ec_key.Q, &ec_key.d, &ec_key.grp.G, minstd_rand, nullptr));
}

bytes ecdsa::pubkey(const mbedtls_ecp_keypair& ec_key) {
  bytes pubkey(FULL_FORM_PUBKEY_LENGTH);
  size_t outlen;

  error.check(mbedtls_ecp_check_pub_priv(&ec_key, &ec_key, minstd_rand, nullptr));

  error.check(mbedtls_ecp_point_write_binary(&ec_key.grp, &ec_key.Q, MBEDTLS_ECP_PF_COMPRESSED, &outlen, pubkey.data(),
                                             pubkey.size()));
  return pubkey;
}

bytes ecdsa::sign(const mbedtls_ecp_keypair& key, const bytes& hash) {
  wrap<mbedtls_mpi> r(mbedtls_mpi_init, mbedtls_mpi_free);
  wrap<mbedtls_mpi> s(mbedtls_mpi_init, mbedtls_mpi_free);

  error.check(mbedtls_ecdsa_sign_det_ext(const_cast<mbedtls_ecp_group*>(&key.grp) /*?*/, &r, &s, &key.d, hash.data(),
                                         hash.size(), MBEDTLS_MD_SHA256, minstd_rand, nullptr));

  bytes sig(MBEDTLS_ECDSA_MAX_LEN);
  size_t sz = 0;
  error.check(ecdsa_signature_to_asn1(&r, &s, sig.data(), &sz));
  // trim
  sig.resize(sz);
  return sig;
}

int ecdsa::verify(const bytes& hash, const bytes& sig, const bytes& pubkey) {
  // context is keypair typedef. needs to be initialised with group and pubkey
  wrap<mbedtls_ecdsa_context> ec_key(mbedtls_ecdsa_init, mbedtls_ecdsa_free);

  // mbedtls_ecdsa_init(&ec_key);
  error.check(mbedtls_ecp_group_load(&ec_key->grp, MBEDTLS_ECP_DP_SECP256K1));
  error.check(mbedtls_ecp_point_read_binary(&ec_key->grp, &ec_key->Q, pubkey.data(), pubkey.size()));

  return mbedtls_ecdsa_read_signature(&ec_key, hash.data(), hash.size(), sig.data(), sig.size());
}

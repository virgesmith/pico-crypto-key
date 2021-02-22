
#include "ecdsa.h"

#include "mbedtls/ecp.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/pk.h"

#include "mbedtls/asn1write.h" // for local ecdsa_signature_to_asn1
#include "mbedtls/error.h" // for local ecdsa_signature_to_asn1

#include <cstdint>
#include <cstring>

namespace {

// copied from ecdsa.c (where its static)
int ecdsa_signature_to_asn1( const mbedtls_mpi *r, const mbedtls_mpi *s,
                                    unsigned char *sig, size_t *slen )
{
  int ret = MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED;
  unsigned char buf[MBEDTLS_ECDSA_MAX_LEN];
  unsigned char *p = buf + sizeof( buf );
  size_t len = 0;

  MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_mpi( &p, buf, s ) );
  MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_mpi( &p, buf, r ) );

  MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_len( &p, buf, len ) );
  MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_tag( &p, buf,
                                      MBEDTLS_ASN1_CONSTRUCTED | MBEDTLS_ASN1_SEQUENCE ) );

  memcpy( sig, p, len );
  *slen = len;

  return( 0 );
}

}

mbedtls_ecp_keypair ecdsa::key(const bytes& rawkey)
{
  mbedtls_ecdsa_context ec_ctx;
  mbedtls_ecdsa_init(&ec_ctx);
  mbedtls_ecp_keypair ec_key;
  mbedtls_ecp_keypair_init(&ec_key);
  int ret = mbedtls_ecp_read_key(MBEDTLS_ECP_DP_SECP256K1, &ec_key, rawkey.data(), rawkey.size());
  ret = mbedtls_ecp_mul(&ec_key.grp, &ec_key.Q, &ec_key.d, &ec_key.grp.G, NULL, NULL);
  return ec_key;
}

bytes ecdsa::pubkey(const mbedtls_ecp_keypair& ec_key)
{
  bytes pubkey(65);
  size_t outlen;

  int ret = mbedtls_ecp_check_pub_priv(&ec_key, &ec_key);
  if (ret != 0)
    return bytes();

  ret = mbedtls_ecp_point_write_binary(&ec_key.grp,
                                       &ec_key.Q,
                                       MBEDTLS_ECP_PF_UNCOMPRESSED,
                                       &outlen,
                                       pubkey.data(),
                                       pubkey.size());
  if (ret != 0)
    return bytes();
  return pubkey;
}

bytes ecdsa::sign(const mbedtls_ecp_keypair& key, const bytes& hash)
{
  mbedtls_mpi r, s;
  mbedtls_mpi_init(&r);
  mbedtls_mpi_init(&s);

  int ret = mbedtls_ecdsa_sign_det_ext(const_cast<mbedtls_ecp_group*>(&key.grp) /*?*/, &r, &s, &key.d,
                                       hash.data(), hash.size(), MBEDTLS_MD_SHA256,
                                       minstd_rand, NULL);
  if (ret != 0)
    return bytes();

  bytes sig(MBEDTLS_ECDSA_MAX_LEN);
  size_t sz = 0;
  ecdsa_signature_to_asn1(&r, &s, sig.data(), &sz);
  // trim
  sig.resize(sz);
  return sig;
}

int ecdsa::verify(const bytes& hash, const bytes& sig, const bytes& pubkey)
{
  mbedtls_ecdsa_context ec_key; // context is keypair typedef. needs to be initialised with group and pubkey
  mbedtls_ecdsa_init(&ec_key);
  int ret = mbedtls_ecp_group_load(&ec_key.grp, MBEDTLS_ECP_DP_SECP256K1);
  if (ret)
    return ret;
  ret = mbedtls_ecp_point_read_binary(&ec_key.grp, &ec_key.Q, pubkey.data(), pubkey.size());
  if (ret)
    return ret;

  ret = mbedtls_ecdsa_read_signature(&ec_key, hash.data(), hash.size(), sig.data(), sig.size());
  return ret;
}

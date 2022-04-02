#include "sha256.h"
#include "serial.h"
#include "error.h"
#include "mbedtls/sha256.h"

namespace {

  ErrorMapper error(ErrorMapper::Context::SHA, {});
}


bytes sha256::hash(const bytes& data)
{
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);

  error.check(mbedtls_sha256_starts(&ctx, 0));

  error.check(mbedtls_sha256_update(&ctx, data.data(), data.size()));

  bytes hash(sha256::LENGTH_BYTES);
  error.check(mbedtls_sha256_finish(&ctx, hash.data()));

  return hash;
}

bytes sha256::hash_stdin()
{
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);

  mbedtls_sha256_starts(&ctx, 0);

  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes s = base64::decode(chunk);
    mbedtls_sha256_update(&ctx, (byte*)&*s.cbegin(), s.size());
  }

  bytes hash(sha256::LENGTH_BYTES);
  mbedtls_sha256_finish(&ctx, hash.data());

  return hash;
}
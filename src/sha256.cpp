#include "sha256.h"
#include "error.h"
#include "usb_cdc.h"

#include "mbedtls/sha256.h"

namespace {
ErrorMapper error(ErrorMapper::Context::SHA, {});
}

bytes sha256::hash(const bytes& data) {
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);

  error.check(mbedtls_sha256_starts(&ctx, 0));

  error.check(mbedtls_sha256_update(&ctx, data.data(), data.size()));

  bytes hash(sha256::LENGTH_BYTES);
  error.check(mbedtls_sha256_finish(&ctx, hash.data()));

  return hash;
}

bytes sha256::hash_in(uint32_t length) {
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);

  mbedtls_sha256_starts(&ctx, 0);

  bytes buffer(cdc::CHUNK_SIZE);

  for (uint32_t total_read = 0; total_read < length;) {
    uint32_t bytes_to_read = std::min(cdc::CHUNK_SIZE, length - total_read);
    uint32_t bytes_read = cdc::read(buffer, bytes_to_read);
    mbedtls_sha256_update(&ctx, buffer.data(), bytes_read);
    total_read += bytes_read;
  }

  bytes hash(sha256::LENGTH_BYTES);
  mbedtls_sha256_finish(&ctx, hash.data());

  return hash;
}
#include "sha256.h"
#include "error.h"
#include "usb_cdc.h"

#include "mbedtls/sha256.h"
#ifdef PICO_RP2350
#include "pico/sha256.h"
#endif

namespace {
ErrorMapper error(ErrorMapper::Context::SHA, {});
}


bytes sha256::hash(const bytes& data) {
#ifdef PICO_RP2350
  pico_sha256_state_t state;
  sha256_result_t result;
  error.check(pico_sha256_try_start(&state, SHA256_BIG_ENDIAN, true));
  pico_sha256_update(&state, data.data(), data.size());
  pico_sha256_finish(&state, &result);
  bytes hash(result.bytes, result.bytes + SHA256_RESULT_BYTES);
#else
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);
  error.check(mbedtls_sha256_starts(&ctx, 0));
  error.check(mbedtls_sha256_update(&ctx, data.data(), data.size()));
  bytes hash(sha256::LENGTH_BYTES);
  error.check(mbedtls_sha256_finish(&ctx, hash.data()));
#endif
  return hash;
}

bytes sha256::hash_in() {
  // 4 byte header containing length of data
  uint32_t length;
  cdc::read(length);
  bytes buffer(cdc::CHUNK_SIZE);

#ifdef PICO_RP2350
  pico_sha256_state_t state;
  sha256_result_t result;
  pico_sha256_try_start(&state, SHA256_BIG_ENDIAN, true);

  for (uint32_t total_read = 0; total_read < length;) {
    uint32_t bytes_to_read = std::min(cdc::CHUNK_SIZE, length - total_read);
    uint32_t bytes_read = cdc::read(buffer, bytes_to_read);
    pico_sha256_update(&state, buffer.data(), bytes_read);
    total_read += bytes_read;
  }

  pico_sha256_finish(&state, &result);
  bytes hash(result.bytes, result.bytes + SHA256_RESULT_BYTES);

#else
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);
  mbedtls_sha256_starts(&ctx, 0);

  for (uint32_t total_read = 0; total_read < length;) {
    uint32_t bytes_to_read = std::min(cdc::CHUNK_SIZE, length - total_read);
    uint32_t bytes_read = cdc::read(buffer, bytes_to_read);
    mbedtls_sha256_update(&ctx, buffer.data(), bytes_read);
    total_read += bytes_read;
  }

  bytes hash(sha256::LENGTH_BYTES);
  mbedtls_sha256_finish(&ctx, hash.data());
#endif
  return hash;
}
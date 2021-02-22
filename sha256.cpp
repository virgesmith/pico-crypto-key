#include "sha256.h"
#include "serial.h"
//#include "sha256_bcon.h"
#include "mbedtls/sha256.h"

// bcon versions
// bytes sha256::hash_stdin()
// {
//   SHA256_CTX ctx;
//   sha256_init(&ctx);
//   for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
//   {
//     bytes s = base64::decode(chunk);
//     sha256_update(&ctx, (byte*)&*s.cbegin(), s.size());
//   }
//   bytes h(SHA256_BLOCK_SIZE);
//   sha256_final(&ctx, h.data());
//   return h;
// }

// bytes sha256::hash(const bytes& data)
// {
//   SHA256_CTX ctx;
//   sha256_init(&ctx);
//   sha256_update(&ctx, data.data(), data.size());
//   bytes h(SHA256_BLOCK_SIZE);
//   sha256_final(&ctx, h.data());
//   return h;
// }

bytes sha256::hash(const bytes& data)
{
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);

  mbedtls_sha256_starts_ret(&ctx, 0);
  mbedtls_sha256_update_ret(&ctx, data.data(), data.size());

  bytes hash(sha256::LENGTH_BYTES);
  mbedtls_sha256_finish_ret(&ctx, hash.data());

  return hash;
}

bytes sha256::hash_stdin()
{
  wrap<mbedtls_sha256_context> ctx(mbedtls_sha256_init, mbedtls_sha256_free);

  mbedtls_sha256_starts_ret(&ctx, 0);

  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes s = base64::decode(chunk);
    mbedtls_sha256_update_ret(&ctx, (byte*)&*s.cbegin(), s.size());
  }

  bytes hash(sha256::LENGTH_BYTES);
  mbedtls_sha256_finish_ret(&ctx, hash.data());

  return hash;
}
#include "sha256.h"
#include "serial.h"
#include "sha256_bcon.h"

bytes sha256::hash()
{
  SHA256_CTX ctx;
  sha256_init(&ctx);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes s = base64::decode(chunk);
    sha256_update(&ctx, (byte*)&*s.cbegin(), s.size());
  }
  bytes h(SHA256_BLOCK_SIZE);
  sha256_final(&ctx, h.data());
  return h;
}

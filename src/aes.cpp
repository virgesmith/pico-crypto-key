
#include "aes.h"
#include "utils.h"
#include "serial.h"
#include "error.h"

#include <string>

// TODO move the serial comms out of this file...

void aes::key(const bytes& raw, mbedtls_aes_context& aes_key)
{
  // according to doc, you use the "enc" function to create a key for both encryption and decryption
  int ret = mbedtls_aes_setkey_enc(&aes_key, raw.data(), 256);
  switch(ret)
  {
    case 0:
      break;
    case MBEDTLS_ERR_AES_INVALID_KEY_LENGTH:
      error_state(ErrorCode::AES | ErrorCode::INVALID_KEY_LENGTH);
    default:
      error_state(ErrorCode::AES | ErrorCode::UNKNOWN);
  }
}

void aes::decrypt_stdin(const mbedtls_aes_context& key)
{
  bytes iv(16, 0);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes c = base64::decode(chunk);
    bytes p(c.size());

    int ret = mbedtls_aes_crypt_cfb8(const_cast<mbedtls_aes_context*>(&key), MBEDTLS_AES_DECRYPT, c.size(), iv.data(), c.data(), p.data());
    if (ret != 0)
    {
      return;
    }
    serial::send(base64::encode(p) + "\n");
  }
}

void aes::encrypt_stdin(const mbedtls_aes_context& key)
{
  bytes iv(16, 0);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes p = base64::decode(chunk);
    bytes c(p.size());

    int ret = mbedtls_aes_crypt_cfb8(const_cast<mbedtls_aes_context*>(&key), MBEDTLS_AES_ENCRYPT, p.size(), iv.data(), p.data(), c.data());
    if (ret != 0)
    {
      return;
    }

    serial::send(base64::encode(c) + "\n");
  }
}

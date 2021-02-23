
#include "aes.h"
#include "utils.h"
#include "serial.h"

#include "aes_bcon.h"

#include <string>

aes::key_t aes::key(const bytes& raw)
{
#ifdef USE_MBEDTLS_AES
  mbedtls_aes_context aes_key;
  mbedtls_aes_init(&aes_key);
  // according to doc, you use the "enc" function to create a key for both encryption and decryption
  mbedtls_aes_setkey_enc(&aes_key, raw.data(), 256);
  return aes_key;
#else
  key_t key_schedule(60);
  aes_key_setup(raw.data(), key_schedule.data(), 256);
  return key_schedule;
#endif
}

void aes::decrypt_stdin(const aes::key_t& key)
{
  bytes iv(16, 0);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes c = base64::decode(chunk);
    bytes p(c.size());

#ifdef USE_MBEDTLS_AES
  int ret = mbedtls_aes_crypt_cfb8(const_cast<key_t*>(&key), MBEDTLS_AES_DECRYPT, c.size(), iv.data(), c.data(), p.data());
  if (ret != 0)
  {
    serial::send("mbedtls_aes_crypt_cfb8 decrypt error"s % ret);
    return;
  }
#else
    aes_decrypt_ctr(c.data(), c.size(), p.data(), key.data(), 256, iv.data());
    increment_iv(iv.data(), iv.size());
#endif
    serial::send(base64::encode(p) + "\n");
  }
}

void aes::encrypt_stdin(const aes::key_t& key)
{
  bytes iv(16, 0);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes p = base64::decode(chunk);
    bytes c(p.size());

#ifdef USE_MBEDTLS_AES
    int ret = mbedtls_aes_crypt_cfb8(const_cast<key_t*>(&key), MBEDTLS_AES_ENCRYPT, p.size(), iv.data(), p.data(), c.data());
    if (ret != 0)
    {
      serial::send("mbedtls_aes_crypt_cfb8 decrypt error"s % ret);
      return;
    }
#else
    aes_encrypt_ctr(p.data(), p.size(), c.data(), key.data(), 256, iv.data());
    increment_iv(iv.data(), iv.size());
#endif

    serial::send(base64::encode(c) + "\n");
  }
}

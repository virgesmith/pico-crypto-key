
#include "aes.h"
#include "error.h"
#include "usb_cdc.h"
#include "utils.h"

#include <string>

namespace {
ErrorMapper error(ErrorMapper::AES, {MBEDTLS_ERR_AES_INVALID_KEY_LENGTH});
}

void aes::key(const bytes& raw, mbedtls_aes_context& aes_key) {
  // according to doc, you use the "enc" function to create a key for both encryption and decryption
  error.check(mbedtls_aes_setkey_enc(&aes_key, raw.data(), KEY_BITS));
}

void aes::decrypt_in(const mbedtls_aes_context& key, uint32_t length) {
  bytes iv(16, 0);

  bytes ciphertext(cdc::CHUNK_SIZE);
  bytes plaintext(cdc::CHUNK_SIZE);

  while (length) {
    uint32_t chunk_length = length < cdc::CHUNK_SIZE ? length : cdc::CHUNK_SIZE;
    uint32_t bytes_read = cdc::read(ciphertext, chunk_length);

    int ret = mbedtls_aes_crypt_cfb8(const_cast<mbedtls_aes_context*>(&key), MBEDTLS_AES_DECRYPT, bytes_read, iv.data(),
                                     ciphertext.data(), plaintext.data());
    if (ret != 0) {
      cdc::write("aes err %%"s % ret);
      return;
    }

    /*bytes_written +=*/cdc::write(plaintext, chunk_length);
    length -= chunk_length;
  }

}

void aes::encrypt_in(const mbedtls_aes_context& key, uint32_t length) {
  bytes iv(16, 0);

  bytes plaintext(cdc::CHUNK_SIZE);
  bytes ciphertext(cdc::CHUNK_SIZE);

  while (length) {
    uint32_t chunk_length = length < cdc::CHUNK_SIZE ? length : cdc::CHUNK_SIZE;
    uint32_t bytes_read = cdc::read(plaintext, chunk_length);

    int ret = mbedtls_aes_crypt_cfb8(const_cast<mbedtls_aes_context*>(&key), MBEDTLS_AES_ENCRYPT, bytes_read, iv.data(),
                                     plaintext.data(), ciphertext.data());
    if (ret != 0) {
      cdc::write("aes err %%"s % ret);
      return;
    }

    /*bytes_written +=*/cdc::write(ciphertext, chunk_length);
    length -= chunk_length;
  }
}

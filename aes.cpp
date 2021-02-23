
#include "aes.h"
#include "utils.h"
#include "serial.h"

#include "aes_bcon.h"

#include <string>


aes::key_t aes::key(const bytes& raw)
{
  key_t key_schedule(60);
  aes_key_setup(raw.data(), key_schedule.data(), 256);
  return key_schedule;
}

void aes::decrypt_stdin(const aes::key_t& key)
{
  bytes iv(16, 0);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes c = base64::decode(chunk);
    bytes p(c.size());

    aes_decrypt_ctr(c.data(), c.size(), p.data(), key.data(), 256, iv.data());
    increment_iv(iv.data(), iv.size());
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

    aes_encrypt_ctr(p.data(), p.size(), c.data(), key.data(), 256, iv.data());
    increment_iv(iv.data(), iv.size());

    serial::send(base64::encode(c) + "\n");
  }
}

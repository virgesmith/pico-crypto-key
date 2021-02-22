#include "sha256.h"
#include "aes.h"
#include "ecdsa.h"
#include "serial.h"
#include "utils.h"

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>


void decrypt(const aes_key_t& key)
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

void encrypt(const aes_key_t& key)
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

// raw private key for AES and ECDSA
bytes genkey()
{
  // 8 byte salt + 8 byte board id -> sha256
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);
  bytes raw{ 0xaa, 0xfe, 0xc0, 0xff, 0xba, 0xda, 0x55, 0x55 };
  raw.insert(raw.end(), id.id, id.id + PICO_UNIQUE_BOARD_ID_SIZE_BYTES);

  return sha256::hash(raw);
}


int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  const bytes& key = genkey();

  const mbedtls_ecp_keypair& ec_key = ecdsa::key(key);

  aes_key_t key_schedule(60);
  aes_key_setup(key.data(), key_schedule.data(), SHA256_BLOCK_SIZE*8);

  for (char cmd = std::getchar(); true; cmd = std::getchar())
  {
    switch (cmd)
    {
      // case 'D':
      // {
      //   serial::send("DBG: mbedtls_ecp_mul ret=%%\n"s % ret);
      //   serial::send("DBG: key=" + base64::encode(key) + "\n");
      //   serial::send("DBG: ec ok=%%\n"s % (mbedtls_ecp_check_pub_priv(&ec_key, &ec_key) == 0));
      //   break;
      // }
      case 'H':
      {
        serial::send("help: TODO"s);
        break;
      }
      case 'k':
      {
        const bytes& pubkey = ecdsa::pubkey(ec_key);
        if (pubkey.empty())
          serial::send("ERROR in ecdsa::pubkey\n");
        else
          serial::send(base64::encode(pubkey) + "\n");
        break;
      }
      case 'h':
      {
        serial::send(base64::encode(sha256::hash_stdin()) + "\n");
        break;
      }
      case 'd':
      {
        decrypt(key_schedule);
        break;
      }
      case 'e':
      {
        encrypt(key_schedule);
        break;
      }
      case 's':
      {
        bytes h = sha256::hash_stdin();
        serial::send(base64::encode(h) + "\n");
        bytes sig = ecdsa::sign(ec_key, h);
        if (sig.empty())
          serial::send("ERROR in ecdsa::sign\n");
        serial::send(base64::encode(sig) + "\n");
        break;
      }
      case 'v':
      {
        bytes hash = base64::decode(serial::recv());
        bytes sig = base64::decode(serial::recv());
        bytes pubkey = base64::decode(serial::recv());
        serial::send("%%\n"s % ecdsa::verify(hash, sig, pubkey));
        break;
      }
      default:
      {
        serial::send("%% not a valid command"s % cmd);
      }
    }
    sleep_ms(250);
  }
}
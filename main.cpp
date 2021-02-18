#include "base64.h"
#include "sha256.h"
#include "aes.h"
#include "serial.h"

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

namespace std
{
// prevents char being casted to int
std::string to_string(char c)
{
  return std::string(1, c);
}

}

template<typename T>
std::string operator%(std::string&& str, T value)
{
  size_t s = str.find("%%");
  if (s != std::string::npos)
  {
    str.replace(s, 2, std::to_string(value));
  }
  return std::move(str);
}

using namespace std::string_literals;


void hash()
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

  serial::send(base64::encode(h) + "\n");
}

void decrypt(const std::vector<uint32_t>& key)
{
  bytes iv{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes c = base64::decode(chunk);
    bytes p(c.size());

    aes_decrypt_ctr(c.data(), c.size(), p.data(), key.data(), 256, iv.data());
    // TODO call increment_iv?

    serial::send(base64::encode(p) + "\n");
  }
}

void encrypt(const std::vector<uint32_t>& key)
{
  bytes iv{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes p = base64::decode(chunk);
    bytes c(p.size());

    aes_encrypt_ctr(p.data(), p.size(), c.data(), key.data(), 256, iv.data());
    // TODO call increment_iv?

    serial::send(base64::encode(c) + "\n");
  }
}

std::vector<uint32_t> genkey()
{
  // 8 byte salt + 8 byte board id -> sha256
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);
  bytes raw{ 0xaa, 0xfe, 0xc0, 0xff, 0x00, 0x00, 0x00, 0x00 };
  raw.insert(raw.end(), id.id, id.id + PICO_UNIQUE_BOARD_ID_SIZE_BYTES);

  SHA256_CTX ctx;
  sha256_init(&ctx);
  sha256_update(&ctx, raw.data(), raw.size());
  bytes key(SHA256_BLOCK_SIZE);
  sha256_final(&ctx, key.data());

  std::vector<uint32_t> key_schedule(60);

  aes_key_setup(key.data(), key_schedule.data(), SHA256_BLOCK_SIZE*8);

  return key_schedule;
}

int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  const std::vector<uint32_t>& key = genkey();

  for (char cmd = std::getchar(); true; cmd = std::getchar())
  {
    switch (cmd)
    {
      // case 'k':
      // {
      //   serial::send(base64::encode(key()) + "\n");
      //   break;
      // }
      case 'h':
      {
        hash();
        break;
      }
      case 'd':
      {
        decrypt(key);
        break;
      }
      case 'e':
      {
        encrypt(key);
        break;
      }
      case 's':
      default:
      {
        serial::send("%% not a valid command"s % cmd);
      }
    }
    sleep_ms(250);
  }
}
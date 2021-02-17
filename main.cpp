#include "base64.h"
#include "sha256.h"
#include "aes.h"
#include "serial.h"

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

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

void decrypt()
{
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes s = base64::decode(chunk);
    for(auto& c: s)
      --c;
    serial::send(base64::encode(s) + "\n");
  }
}

void encrypt()
{
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes s = base64::decode(chunk);
    for(auto& c: s)
      ++c;
    serial::send(base64::encode(s) + "\n");
  }
}

int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  for (char cmd = std::getchar(); true; cmd = std::getchar())
  {
    switch (cmd)
    {
      case 'h':
      {
        hash();
        break;
      }
      case 'd':
      {
        decrypt();
        break;
      }
      case 'e':
      {
        encrypt();
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
#include "base64.h"
#include "sha256.h"
#include "comms.h"

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


std::string hash()
{
  SHA256_CTX ctx;
  sha256_init(&ctx);
  for(std::string chunk = recv(); !chunk.empty(); chunk = recv())
  {
    bytes s = base64::decode(chunk);
    sha256_update(&ctx, (byte*)&*s.cbegin(), s.size());
  }
  bytes h(SHA256_BLOCK_SIZE);
  sha256_final(&ctx, h.data());

  return base64::encode(h);
}

int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  char cmd;
  for (;;)
  {
    cmd = std::getchar();
    if (cmd == 'h')
    {
      send(hash() + "\n");
      //stdio_flush();
    }
    sleep_ms(250);
  }
}
#include "base64.h"
#include "sha256.h"
#include "comms.h"

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

//#include <cstdio>
//#include <stdio.h>
#include <unistd.h>

const uint LED_PIN = 25;

void flash(int times, int ms)
{
  for (int i = 0; i < times; ++i)
  {
    gpio_put(LED_PIN, 1);
    sleep_ms(ms);
    gpio_put(LED_PIN, 0);
    sleep_ms(ms);
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

int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  //setmode(STDOUT_FILENO, O_BINARY);
  //freopen(NULL, "wb", stdout);
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  SHA256_CTX ctx;

  char cmd;
  for (;;)
  {
    cmd = std::getchar();
    if (cmd == 'h')
    {
      std::string b64 = recv();
      bytes s = base64::decode(b64);
      send("got %% bytes -> %% bytes\n"s % b64.size() % s.size());

      sha256_init(&ctx);
      sha256_update(&ctx, (byte*)&*s.cbegin(), s.size());
      bytes h(SHA256_BLOCK_SIZE);
      sha256_final(&ctx, h.data());

      std::string msg = base64::encode(h) + "\n";
      send(msg);
      flash(1, 500);
      stdio_flush();
    }
    sleep_ms(250);
  }
}
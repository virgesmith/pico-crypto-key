#include "sha256.h"
#include "comms.h"

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

#include <cstdio>
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

std::string toHex(const std::vector<uint8_t>& a)
{
  static const char hex[] = "0123456789abcdef";
  std::string s;
  for (uint8_t i: a)
  {
    s.push_back(hex[i >> 4]);
    s.push_back(hex[i & 15]);
  }
  return s;
}

using namespace std::string_literals;

int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  SHA256_CTX ctx;

  uint32_t size;
  char* sbuf = reinterpret_cast<char*>(&size);
  char cmd;
  for (;;)
  {
    read(STDIN_FILENO, &cmd, 1);
    if (cmd == 'h')
    {
      ssize_t bytes_read = read(STDIN_FILENO, sbuf, sizeof(uint32_t));

      std::string msg = "read %% bytes\n"s % bytes_read;
      // write(STDIN_FILENO, msg.data(), msg.size());
      std::printf(msg.c_str());
      //send(msg);

      msg = "waiting for %% bytes...\n"s % size;
      std::printf(msg.c_str());
      if (size)
      {
        std::vector<BYTE> f(size);
        bytes_read = read(STDIN_FILENO, &*f.begin(), size);
        std::printf("got %d bytes\n", bytes_read);

        // TODO check bytes_read==size
        sha256_init(&ctx);
        sha256_update(&ctx, &*f.cbegin(), bytes_read);
        std::vector<BYTE> h(SHA256_BLOCK_SIZE);
        sha256_final(&ctx, h.data());

        msg = toHex(h) + "\n";
        std::printf(msg.c_str());
      }
      flash(1, 500);
      //sleep_ms(250);
    }
  }
}

#include "serial.h"
#include "pico/stdlib.h"

// can't get binary to work

std::string serial::recv()
{
  std::string s;
  gpio_put(LED_PIN, 1);
  for (char c = getchar(); c != '\n'; c = getchar())
  {
    s.push_back(c);
  }
  gpio_put(LED_PIN, 0);
  return s;
}

bool serial::send(const std::string& s)
{
  gpio_put(LED_PIN, 1);
  printf(s.c_str());
  gpio_put(LED_PIN, 0);
  return true;
}

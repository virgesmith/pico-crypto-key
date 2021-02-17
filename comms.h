#pragma once

#include "pico/stdlib.h"

#include <string>

const uint LED_PIN = 25;

inline void flash(int times, int ms)
{
  for (int i = 0; i < times; ++i)
  {
    gpio_put(LED_PIN, 1);
    sleep_ms(ms);
    gpio_put(LED_PIN, 0);
    sleep_ms(ms);
  }
}

// can't get binary to work

inline std::string recv()
{
  std::string s;
  gpio_put(LED_PIN, 1);
  for(char c = getchar(); c != '\n'; c = getchar())
  {
    s.push_back(c);
  }
  gpio_put(LED_PIN, 0);
  return s;
}

inline bool send(const std::string& s)
{
  printf(s.c_str());
  return true;
}

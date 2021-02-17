#pragma once

#include "pico/stdlib.h"

#include <string>

const uint LED_PIN = 25;

// can't get binary to work

namespace serial
{

inline std::string recv()
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

inline bool send(const std::string& s)
{
  gpio_put(LED_PIN, 1);
  printf(s.c_str());
  gpio_put(LED_PIN, 0);
  return true;
}

}
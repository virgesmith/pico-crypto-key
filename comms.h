#pragma once

#include "pico/stdlib.h"

#include <string>

// can't get binary to work

inline std::string recv()
{
  std::string s;
  for(;;)
  {
    char c = getchar();
    if (c == '\n') break;
    s.push_back(c);
  }
  return s;
}

inline bool send(const std::string& s)
{
  printf(s.c_str());
  return true;
}

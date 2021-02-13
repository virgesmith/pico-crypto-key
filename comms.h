#pragma once

#include <string>
#include <unistd.h>

inline bool send(const std::string& s)
{
  char null = 0;
  ssize_t res = write(STDIN_FILENO, s.data(), s.size());
  write(STDIN_FILENO, &null, 1);
  return res != -1;
}


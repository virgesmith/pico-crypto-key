#pragma once

#include <string>
#include <vector>

typedef uint8_t byte;
typedef std::vector<byte> bytes;

// rng for mbedtls
extern "C" int minstd_rand(void*, byte* p, size_t n);

namespace std
{
// prevents char being casted to int
std::string to_string(char c);
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


namespace base64 {

std::string encode(const bytes& b);

bytes decode(const std::string& s);

}



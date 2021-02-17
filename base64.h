#pragma once

#include <string>
#include <vector>

typedef uint8_t byte;
typedef std::vector<byte> bytes;

namespace base64 {

std::string encode(const bytes& b);

bytes decode(const std::string& s);

}




#include "utils.h"

namespace {
  const char base64Digits[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
  const byte INVALID = 255;

  bytes base64Lookup()
  {
    byte idx = 255; // this signifies invalid
    bytes lookup(256, idx);
    for (size_t i = 0; i < sizeof(base64Digits); ++i)
    {
      lookup[base64Digits[i]] = ++idx;
    }
    return lookup;
  }
}

// string construction

// prevents char being casted to int
std::string std::to_string(char c)
{
  return std::string(1, c);
}

/* Base 64 de/encoding translated from java implementation here https://en.wikipedia.org/wiki/Base64 */

bytes base64::decode(const std::string& input)
{
  static const bytes lookup = base64Lookup();

  if (input.size() % 4 != 0)
  {
    return bytes(); //throw std::runtime_error("Invalid base64 input");
  }
  //byte decoded[] = new byte[((input.length() * 3) / 4) - (input.indexOf('=') > 0 ? (input.length() - input.indexOf('=')) : 0)];
  size_t eqpos = input.find('=', input.size() - 2) == std::string::npos ? input.size() : input.find('=', input.size() - 2);
  size_t nequals = input.size() - eqpos;
  bytes decoded(input.length() * 3 / 4 - nequals, 0);
  size_t j = 0;
  byte b[4];
  for (size_t i = 0; i < input.size(); i += 4)
  {
    b[0] = lookup[input[i]];
    b[1] = lookup[input[i + 1]];
    b[2] = lookup[input[i + 2]];
    b[3] = lookup[input[i + 3]];
    if (b[0] == INVALID || b[1] == INVALID  || b[2] == INVALID  || b[3] == INVALID)
    {
      return bytes(); //throw std::runtime_error("invalid digit in base64 string");
    }
    decoded[j++] = ((b[0] << 2) | (b[1] >> 4));
    if (b[2] < 64)
    {
      decoded[j++] = ((b[1] << 4) | (b[2] >> 2));
      if (b[3] < 64)
      {
        decoded[j++] = ((b[2] << 6) | b[3]);
      }
    }
  }
  return decoded;
}

std::string base64::encode(const bytes& in)
{
  std::string out;
  out.reserve(in.size() * 4 / 3);

  byte b;
  for (size_t i = 0; i < in.size(); i += 3)
  {
    b = (in[i] & 0xFC) >> 2;
    out.push_back(base64Digits[b]);
    b = (in[i] & 0x03) << 4;
    if ((i + 1) < in.size())
    {
      b |= (in[i + 1] & 0xF0) >> 4;
      out.push_back(base64Digits[b]);
      b = (in[i + 1] & 0x0F) << 2;
      if ((i + 2) < in.size())
      {
        b |= (in[i + 2] & 0xC0) >> 6;
        out.push_back(base64Digits[b]);
        b = in[i + 2] & 0x3F;
        out.push_back(base64Digits[b]);
      }
      else
      {
        out.push_back(base64Digits[b]);
        out.push_back('=');
      }
    }
    else
    {
      out.push_back(base64Digits[b]);
      out.push_back('=');
      out.push_back('=');
    }
  }
  return out;
}








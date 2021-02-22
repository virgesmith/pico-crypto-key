#pragma once

#include <string>
#include <vector>

typedef uint8_t byte;
typedef std::vector<byte> bytes;

typedef std::vector<uint32_t> aes_key_t;

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

// RAII memory-safe wrapper for C structures with explicit init/free functions
template<typename T>
class wrap final
{
public:
  typedef void (*f_init_t)(T*);
  typedef void (*f_free_t)(T*);

  wrap(f_init_t init, f_free_t free) : m_struct(), m_deleter(free)
  {
    init(&m_struct);
  }

  ~wrap()
  {
    m_deleter(&m_struct);
  }

  // disable any (shallow) copy or assignment)
  wrap(const wrap&) = delete;
  wrap& operator=(const wrap&) = delete;
  wrap(wrap&&) = delete;
  wrap& operator=(wrap&&) = delete;

  T* operator &() { return &m_struct; }
  const T* operator &() const { return &m_struct; }

  // TODO can this be done better syntactically?
  T& operator()() { return m_struct; }
  const T& operator()() const { return m_struct; }

private:
  T m_struct;
  f_free_t m_deleter;
};

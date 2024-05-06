#pragma once

#include <string>
#include <vector>
#include <cstdint>

typedef uint8_t byte;
typedef std::vector<byte> bytes;

namespace std
{
// force byte to print as character 
inline std::string to_string(uint8_t c)
{
  return std::string(1, c);
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

using namespace std::string_literals;

// RAII memory-safe(r) wrapper for C structures with explicit init/free functions
template <typename T> class wrap final {
public:
  typedef T value_type;
  typedef void (*f_init_t)(T*);
  typedef void (*f_free_t)(T*);

  wrap(f_init_t init, f_free_t free) : m_struct(), m_deleter(free) { init(&m_struct); }

  ~wrap() { m_deleter(&m_struct); }

  // disable any (shallow) copy or assignment)
  wrap(const wrap&) = delete;
  wrap& operator=(const wrap&) = delete;
  wrap(wrap&&) = delete;
  wrap& operator=(wrap&&) = delete;

  value_type* operator&() { return &m_struct; }
  const value_type* operator&() const { return &m_struct; }

  value_type* operator->() { return &m_struct; }
  const value_type* operator->() const { return &m_struct; }

  // can this be done better syntactically?
  value_type& operator*() { return m_struct; }
  const value_type& operator*() const { return m_struct; }

private:
  T m_struct;
  f_free_t m_deleter;
};

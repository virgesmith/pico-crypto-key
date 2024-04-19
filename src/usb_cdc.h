#include "utils.h"

#include "tusb.h"

#include <algorithm>
#include <string>

namespace cdc {

constexpr uint32_t CHUNK_SIZE = 2048;

// Read length (no checking for buffer overrun)
uint32_t read_impl(byte* buffer, uint32_t length);

// Read length into buffer without overrun
uint32_t read(bytes& buffer, uint32_t length);

// Read into type
template <typename T> 
bool read(T& dest) {
  return read_impl(reinterpret_cast<uint8_t*>(&dest), sizeof(T)) == sizeof(T);
}

// specialise for bytes
template <> bool cdc::read(bytes& b);

// Write bytes (without flushing?)
uint32_t write_impl(const byte* buffer, uint32_t buffer_size);

// Write part of a byte buffer
uint32_t write(const bytes& buffer, uint32_t length);

// Write a C string
bool write(const char* str);

// Write a type (specialised for bytes/string)
template <typename T> 
bool write(const T& src) {
  return write_impl(reinterpret_cast<const uint8_t*>(&src), sizeof(T)) == sizeof(T);
}

template<>
bool cdc::write(const bytes& b);

template<>
bool cdc::write(const std::string& s);


} // namespace cdc
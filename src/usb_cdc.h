#include "utils.h"

#include "tusb.h"

#include <algorithm>
#include <string>

namespace cdc {

constexpr uint32_t CHUNK_SIZE = 2048;

extern bytes read_buffer;
//extern bytes write_buffer;

// Read length (no checking for buffer overrun)
uint32_t read_impl(byte* buffer, uint32_t length);

// Read length into buffer without overrun
inline uint32_t read(bytes& buffer, uint32_t length) {
  return read_impl(buffer.data(), std::min((uint32_t)buffer.size(), length));
}

// Read into type (specialised for bytes)
template <typename T> bool read(T& dest) {
  return read_impl(reinterpret_cast<uint8_t*>(&dest), sizeof(T)) == sizeof(T);
}

// Write bytes (without flushing?)
uint32_t write_impl(const byte* buffer, uint32_t buffer_size);

// Write a byte buffer
inline uint32_t write(const bytes& buffer) {
  return write_impl(buffer.data(), (uint32_t)buffer.size());
}

// Write part of a byte buffer
inline uint32_t write(const bytes& buffer, uint32_t length) {
  return write_impl(buffer.data(), std::min((uint32_t)buffer.size(), length));
}

// Write a string
inline uint32_t write(const std::string& s) {
  return write_impl(reinterpret_cast<const uint8_t*>(s.data()), s.size());
}

// inline uint32_t write(const bytes& b) {
//   return write(reinterpret_cast<const uint8_t*>(b.data()), b.size());
// }

} // namespace cdc
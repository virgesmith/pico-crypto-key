#include "usb_cdc.h"
#include "tusb.h"

#include <algorithm>

uint32_t cdc::read_impl(byte* buffer, uint32_t buffer_size) {
  uint32_t buffer_pos = 0;
  while (buffer_pos < buffer_size) {
    uint32_t bytes_to_read = std::min(tud_cdc_available(), buffer_size - buffer_pos);
    if (bytes_to_read) {
      buffer_pos += tud_cdc_read(buffer + buffer_pos, bytes_to_read);
    }
    tud_task();
  }
  return buffer_pos;
}

uint32_t cdc::read(bytes& b, uint32_t length) { return cdc::read_impl(b.data(), std::min((uint32_t)b.size(), length)); }

// specialise for bytes
template <> bool cdc::read(bytes& b) { return read_impl(b.data(), b.size()) == b.size(); }

uint32_t cdc::write_impl(const byte* buffer, uint32_t buffer_size) {
  uint32_t buffer_pos = 0;
  while (buffer_pos < buffer_size) {
    uint32_t bytes_to_write = std::min(tud_cdc_write_available(), buffer_size - buffer_pos);

    if (bytes_to_write) {
      buffer_pos += tud_cdc_write(buffer + buffer_pos, bytes_to_write);
    }
    tud_task();
    tud_cdc_write_flush();
  }
  return buffer_pos;
}

uint32_t cdc::write(const bytes& b, uint32_t length) {
  return cdc::write_impl(b.data(), std::min((uint32_t)b.size(), length));
}

bool cdc::write(const char* str) {
  return cdc::write_impl(reinterpret_cast<const uint8_t*>(str), strnlen(str, cdc::CHUNK_SIZE)) == strnlen(str, cdc::CHUNK_SIZE);
}

template <> bool cdc::write(const bytes& b) { return cdc::write_impl(b.data(), b.size()) == b.size(); }

template <> bool cdc::write(const std::string& s) {
  return cdc::write_impl(reinterpret_cast<const uint8_t*>(s.data()), s.size()) == s.size();
}

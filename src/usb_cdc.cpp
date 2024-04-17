#include "usb_cdc.h"
#include "tusb.h"

#include <algorithm>

bytes cdc::read_buffer(CHUNK_SIZE);
//bytes cdc::write_buffer(CHUNK_SIZE);

// Read bytes (blocks until buffer_size is reached)
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

// specialise for bytes
template<> bool cdc::read(bytes& b) {
  return read_impl(b.data(), b.size()) == b.size();
}


uint32_t cdc::write_impl(const byte* buffer, uint32_t buffer_size) {
  uint32_t buffer_pos = 0;
  while (buffer_pos < buffer_size) {
    uint32_t bytes_to_write =
        std::min(tud_cdc_write_available(), buffer_size - buffer_pos);

    if (bytes_to_write) {
      buffer_pos += tud_cdc_write(buffer + buffer_pos, bytes_to_write);
    }
    tud_task();
    tud_cdc_write_flush();
  }
  return buffer_pos;
}


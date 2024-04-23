
#include "flash.h"

#include <algorithm>
#include <pico/stdlib.h>

namespace {
const uint32_t storage_offset = PICO_FLASH_SIZE_BYTES - FLASH_SECTOR_SIZE; // last sector
const uint8_t* storage_address = reinterpret_cast<uint8_t*>(XIP_BASE + storage_offset);
} // namespace

void flash::write(const bytes& b) {
  uint32_t length = std::min(b.size(), FLASH_SECTOR_SIZE);
  uint32_t ints = save_and_disable_interrupts();
  flash_range_erase(storage_offset, length);
  flash_range_program(storage_offset, b.data(), length);
  restore_interrupts(ints);
}

bytes flash::read(size_t length) {
  length = std::min(length, FLASH_SECTOR_SIZE);
  return bytes(storage_address, storage_address + length);
}


#include "flash.h"

#include <hardware/flash.h>
#include <hardware/sync.h> // for interrupts

#include <algorithm>
#include <pico/stdlib.h>

namespace {
// bootrom bug workaround for RP2350 stops the use of the final flash sector, see here
// https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf#%5B%7B%22num%22%3A1341%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C115%2C198.974%2Cnull%5D
// workaround is to use the penultimate sector
#ifdef PICO_RP2350
const uint32_t sectors_from_end = 2;
#else
const uint32_t sectors_from_end = 1;
#endif
const uint32_t storage_offset = PICO_FLASH_SIZE_BYTES - sectors_from_end * FLASH_SECTOR_SIZE;
const uint8_t* storage_address = reinterpret_cast<uint8_t*>(XIP_BASE + storage_offset);
} // namespace

uint32_t flash::write(const bytes& b) {
  uint32_t length = std::min(b.size(), FLASH_SECTOR_SIZE);
  uint32_t ints = save_and_disable_interrupts();
  flash_range_erase(storage_offset, length);
  flash_range_program(storage_offset, b.data(), length);
  restore_interrupts(ints);
  // now read to confirm
  bytes check = flash::read(length);
  return b == check ? 0 : -1u; // this will be nonzero if b longer than FLASH_SECTOR_SIZE
}

bytes flash::read(size_t length) {
  length = std::min(length, FLASH_SECTOR_SIZE);
  return bytes(storage_address, storage_address + length);
}

#include "flash.h"
#include "sha256.h"
#include "usb_cdc.h"

#include "pin.h"

namespace {
const bytes salt = {0x19, 0x93, 0x76, 0x02, 0x45, 0x4a, 0xbc, 0xde};
}

bool pin::check() {
  bytes expected = flash::read(32);
  uint32_t size;
  cdc::read(size);
  bytes pin(size);
  cdc::read(pin);
  pin.reserve(pin.size() + salt.size());
  pin.insert(pin.end(), salt.begin(), salt.end());
  bytes h = sha256::hash(pin);
  return h == expected;
}

uint32_t pin::set() {
  uint32_t size;
  cdc::read(size);
  bytes pin(size);
  cdc::read(pin);
  pin.reserve(pin.size() + 8);
  pin.insert(pin.end(), salt.begin(), salt.end());
  bytes h = sha256::hash(pin);
  return flash::write(h);
}

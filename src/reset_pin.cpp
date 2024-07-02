#include "utils.h"
#include "flash.h"
#include "board.h"

#include "pico/stdlib.h"

int main() {
  led::init();
  // this is SHA256 of "pico" + salt
  const bytes expected {
    0x1b, 0x7a, 0x8f, 0x3, 0xae, 0xb8, 0x16, 0x6a, 0xbd, 0x1d, 0x4d, 0xa3, 0x65, 0xe2, 0x4, 0x3d, 0xab, 0xd1, 0xed,
        0xd5, 0xd0, 0x9a, 0xb1, 0x79, 0x6c, 0xeb, 0x5, 0x96, 0x1d, 0x75, 0xcc, 0xde
  };

  const size_t length = expected.size();
  flash::write(expected);
  bytes check = flash::read(length);
  bool ok = check == expected;

  if (ok) {
    // LED off
    for(;;) {
      sleep_ms(1000);
    }

  } else {
    for(;;) {
      led::on(led::RED);
      sleep_ms(500);
      led::off();
      sleep_ms(500);
    }
  }
}
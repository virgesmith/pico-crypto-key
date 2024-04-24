#include "error.h"

#include "pico/stdlib.h"

#include <algorithm>

namespace {
constexpr int LONG_FLASH_MS = 500;
constexpr int SHORT_FLASH_MS = 250;
constexpr int PAUSE_MS = 250;
}

void ErrorMapper::check(int ret) {
  if (ret == 0)
    return;
  auto it = std::find(states.begin(), states.end(), ret);
  enter(it == states.end() ? 0 : it - states.begin() + 1);
}

void ErrorMapper::enter(int code) {
  for (;;) {
    for (int i = 0; i < (int)context; ++i) {
      gpio_put(PICO_DEFAULT_LED_PIN, 1);
      sleep_ms(LONG_FLASH_MS);
      gpio_put(PICO_DEFAULT_LED_PIN, 0);
      sleep_ms(PAUSE_MS);
    }

    // code 0 is unknown error
    for (int i = 0; i < code; ++i) {
      gpio_put(PICO_DEFAULT_LED_PIN, 1);
      sleep_ms(SHORT_FLASH_MS);
      gpio_put(PICO_DEFAULT_LED_PIN, 0);
      sleep_ms(PAUSE_MS);
    }
  }
}

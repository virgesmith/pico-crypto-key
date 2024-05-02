#include "board.h"
#include "pico/time.h"

// Pico W LED is on the wifi chip and requires cyw43 driver and its dependencies
// to function (wifi is not enabled)
#if defined(BOARD_pico_w)

#include "pico/cyw43_arch.h"

bool led::init() {
  auto res = cyw43_arch_init();
  led::on();
  sleep_ms(100);
  led::off();
  return res == 0;
}

void led::on() { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1); }
void led::off() { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0); }

#elif defined(BOARD_pico)

#include "pico/stdlib.h"

bool led::init() {
  gpio_init(PICO_DEFAULT_LED_PIN);
  gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
  led::on();
  sleep_ms(100);
  led::off();
  return true;
}

void led::on() { gpio_put(PICO_DEFAULT_LED_PIN, 1); }
void led::off() { gpio_put(PICO_DEFAULT_LED_PIN, 0); }

#else

#error Board not specified, set PICO_BOARD to either pico or pico_w

#endif

namespace {
uint64_t time_offset_ms = 0u;
}

// uint64_t get_time_offset_ms() { return time_offset_ms; }

void set_time_offset(uint64_t unix_timestamp_ms) {
  time_offset_ms = unix_timestamp_ms - to_ms_since_boot(get_absolute_time());
}

uint64_t get_time_ms() {
  // absolute_time_t is a struct in debug mode, uint64_t otherwise
  absolute_time_t t = get_absolute_time();
#ifdef NDEBUG
  return time_offset_ms + t / 1000;
#else
  return time_offset_ms + t._private_us_since_boot / 1000;
#endif
}

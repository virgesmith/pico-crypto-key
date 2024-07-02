#include "board.h"
#include "pico/time.h"

#if defined(BOARD_pimoroni_tiny2040_2mb)

bool led::init() {
  gpio_init(TINY2040_LED_R_PIN);
  gpio_init(TINY2040_LED_G_PIN);
  gpio_init(TINY2040_LED_B_PIN);
  gpio_set_dir(TINY2040_LED_R_PIN, GPIO_OUT);
  gpio_set_dir(TINY2040_LED_G_PIN, GPIO_OUT);
  gpio_set_dir(TINY2040_LED_B_PIN, GPIO_OUT);
  led::on(led::GREEN);
  sleep_ms(100);
  led::off();
  return true;
}

void led::on(Colour c) {
  if (c & Colour::RED)
    gpio_put(TINY2040_LED_R_PIN, 0);
  if (c & Colour::GREEN)
    gpio_put(TINY2040_LED_G_PIN, 0);
  if (c & Colour::BLUE)
    gpio_put(TINY2040_LED_B_PIN, 0);
}

void led::off() {
  gpio_put(TINY2040_LED_R_PIN, 1);
  gpio_put(TINY2040_LED_G_PIN, 1);
  gpio_put(TINY2040_LED_B_PIN, 1);
}

// Pico W LED is on the wifi chip and requires cyw43 driver and its dependencies
// to function (wifi is not enabled)
#elif defined(BOARD_pico_w)

#include "pico/cyw43_arch.h"

bool led::init() {
  auto res = cyw43_arch_init();
  led::on(led::GREEN);
  sleep_ms(100);
  led::off();
  return res == 0;
}

// pico W only has geen LED
void led::on(Colour) { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1); }
void led::off() { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0); }

#else // default to BOARD_pico

#include "pico/stdlib.h"

bool led::init() {
  gpio_init(PICO_DEFAULT_LED_PIN);
  gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
  led::on(led::GREEN);
  sleep_ms(100);
  led::off();
  return true;
}

// pico only has geen LED
void led::on(Colour) { gpio_put(PICO_DEFAULT_LED_PIN, 1); }
void led::off() { gpio_put(PICO_DEFAULT_LED_PIN, 0); }

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

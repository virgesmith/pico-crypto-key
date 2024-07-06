#include "board.h"
#include "pico/time.h"

namespace {
constexpr int LONG_FLASH_MS = 500;
constexpr int SHORT_FLASH_MS = 250;
constexpr int PAUSE_MS = 250;
} // namespace

#if defined(BOARD_pimoroni_tiny2040_2mb)

namespace {

enum Colour { RED = 1, GREEN = 2, BLUE = 4, WHITE = RED & GREEN & BLUE };

void led_on(Colour c) {
  if (c & RED)
    gpio_put(TINY2040_LED_R_PIN, 0);
  if (c & GREEN)
    gpio_put(TINY2040_LED_G_PIN, 0);
  if (c & BLUE)
    gpio_put(TINY2040_LED_B_PIN, 0);
}

void led_off() {
  gpio_put(TINY2040_LED_R_PIN, 1);
  gpio_put(TINY2040_LED_G_PIN, 1);
  gpio_put(TINY2040_LED_B_PIN, 1);
}

} // namespace

bool board::init() {
  gpio_init(TINY2040_LED_R_PIN);
  gpio_init(TINY2040_LED_G_PIN);
  gpio_init(TINY2040_LED_B_PIN);
  gpio_set_dir(TINY2040_LED_R_PIN, GPIO_OUT);
  gpio_set_dir(TINY2040_LED_G_PIN, GPIO_OUT);
  gpio_set_dir(TINY2040_LED_B_PIN, GPIO_OUT);
  led_on(WHITE);
  sleep_ms(100);
  led_off();
  return true;
}

void board::ready() {
  led_off();
  led_on(GREEN);
}

void board::busy() {
  led_off();
  led_on(BLUE);
}

void board::invalid() {
  led_off();
  led_on(RED);
}

void board::error(int context, int code) {
  for (int i = 0; i < (int)context; ++i) {
    led_on(RED);
    sleep_ms(LONG_FLASH_MS);
    led_off();
    sleep_ms(PAUSE_MS);
  }
  // code 0 is unknown error
  for (int i = 0; i < code; ++i) {
    led_on(RED);
    sleep_ms(SHORT_FLASH_MS);
    led_off();
    sleep_ms(PAUSE_MS);
  }
}

void board::clear() { led_off(); }

// Pico W LED is on the wifi chip and requires cyw43 driver and its dependencies
// to function (wifi is not enabled)
#elif defined(BOARD_pico_w)

#include "pico/cyw43_arch.h"

namespace {
// pico W only has geen LED
void led_on() { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1); }
void led_off() { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0); }
} // namespace

bool board::init() {
  auto res = cyw43_arch_init();
  led_on();
  sleep_ms(100);
  led_off();
  return res == 0;
}

void board::ready() { led_off(); }

void board::busy() { led_on(); }

void board::invalid() { led_off(); }

void board::error(int context, int code) {
  for (int i = 0; i < (int)context; ++i) {
    led_on();
    sleep_ms(LONG_FLASH_MS);
    led_off();
    sleep_ms(PAUSE_MS);
  }
  // code 0 is unknown error
  for (int i = 0; i < code; ++i) {
    led_on();
    sleep_ms(SHORT_FLASH_MS);
    led_off();
    sleep_ms(PAUSE_MS);
  }
}

void board::clear() { led_off(); }

#else // default to BOARD_pico

#include "pico/stdlib.h"

namespace {
// pico only has geen LED
void led_on() { gpio_put(PICO_DEFAULT_LED_PIN, 1); }
void led_off() { gpio_put(PICO_DEFAULT_LED_PIN, 0); }
} // namespace

bool board::init() {
  gpio_init(PICO_DEFAULT_LED_PIN);
  gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
  led_on();
  sleep_ms(100);
  led_off();
  return true;
}

void board::ready() { led_off(); }

void board::busy() { led_on(); }

void board::invalid() { led_off(); }

void board::error(int context, int code) {
  for (int i = 0; i < (int)context; ++i) {
    led_on();
    sleep_ms(LONG_FLASH_MS);
    led_off();
    sleep_ms(PAUSE_MS);
  }
  // code 0 is unknown error
  for (int i = 0; i < code; ++i) {
    led_on();
    sleep_ms(SHORT_FLASH_MS);
    led_off();
    sleep_ms(PAUSE_MS);
  }
}

void board::clear() { led_off(); }

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

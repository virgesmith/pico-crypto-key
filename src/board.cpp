#include "board.h"

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

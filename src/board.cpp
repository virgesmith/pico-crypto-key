#include "board.h"

// Pico W LED is on the wifi chip and requires cyw43 driver and its dependencies
// to function, so is not supported. LED aside, this binary will work on a Pico W

#include "pico/stdlib.h"

bool led::init()
{
  gpio_init(PICO_DEFAULT_LED_PIN);
  gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
  led::on();
  sleep_ms(100);
  led::off();
  return true;
}

void led::on() { gpio_put(PICO_DEFAULT_LED_PIN, 1); }
void led::off() { gpio_put(PICO_DEFAULT_LED_PIN, 0); }




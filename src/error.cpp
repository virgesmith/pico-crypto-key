#include "error.h"
#include "device.h"

#include "pico/stdlib.h"


void error_state(int e)
{
  int major = e / 8;
  int minor = e % 8;
  for (;;)
  {
    for (int i = 0; i < major; ++i)
    {
      gpio_put(LED_PIN, 1);
      sleep_ms(200);
      gpio_put(LED_PIN, 0);
      sleep_ms(200);
    }
    sleep_ms(2000-major*200);
    for (int i = 0; i < minor; ++i)
    {
      gpio_put(LED_PIN, 1);
      sleep_ms(200);
      gpio_put(LED_PIN, 0);
      sleep_ms(200);
    }
    sleep_ms(2000-minor*200);
  }
}

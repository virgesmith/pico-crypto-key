#include "error.h"
#include "device.h"

#include "pico/stdlib.h"

#include <algorithm>


void ErrorMapper::check(int ret)
{
  if (ret == 0)
    return;
  auto it = std::find(states.begin(), states.end(), ret);
  enter(it == states.end() ? 0 : it - states.begin() + 1);
}


void ErrorMapper::enter(int code)
{
  for (;;)
  {
    for (int i = 0; i < (int)context; ++i)
    {
      gpio_put(LED_PIN, 1);
      sleep_ms(200);
      gpio_put(LED_PIN, 0);
      sleep_ms(200);
    }
    sleep_ms(2000 - (int)context * 200);

    // code 0 is unknown error
    for (int i = 0; i < code; ++i)
    {
      gpio_put(LED_PIN, 1);
      sleep_ms(200);
      gpio_put(LED_PIN, 0);
      sleep_ms(200);
    }
    sleep_ms(2000 - code * 200);
  }
}

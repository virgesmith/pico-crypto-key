#pragma once

#include "pico/stdlib.h"

namespace led {
  bool init();
  void on();
  void off();
}

uint64_t get_time_offset_ms();

void set_time_offset(uint64_t unix_timestamp_ms);

uint64_t get_time_ms();

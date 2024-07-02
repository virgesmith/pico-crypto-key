#pragma once

#include "pico/stdlib.h"

namespace led {

// support multicoloured LEDs
enum Colour { RED = 1, GREEN = 2, BLUE = 4, WHITE = RED & GREEN & BLUE };

bool init();
void on(Colour c);
void off();
} // namespace led

// round timestamps to minute for auth purposes
inline uint64_t AUTH_TIME_VALIDITY_MS = 60'000;

void set_time_offset(uint64_t unix_timestamp_ms);

uint64_t get_time_ms();
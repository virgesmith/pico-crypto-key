#pragma once

#include "pico/stdlib.h"

// namespace board {

// // support multicoloured LEDs

// void on(Colour c);
// void off();
// } // namespace led

// round timestamps to minute for auth purposes
inline uint64_t AUTH_TIME_VALIDITY_MS = 60'000;

void set_time_offset(uint64_t unix_timestamp_ms);

uint64_t get_time_ms();

// board-specific display (allows for different LEDs or even screen)
namespace board {

bool init();

void ready();

void busy();

void invalid();

void error(int context, int code);

void clear();

};
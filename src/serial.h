#pragma once

#include "pico/stdlib.h"

#include <string>

extern const uint LED_PIN;

namespace serial
{

std::string recv();

bool send(const std::string& s);

}
#pragma once

#include "utils.h"

#include <hardware/flash.h>
#include <hardware/sync.h> // for interrupts

namespace flash {
void write(const bytes& b);
bytes read(size_t length);
} // namespace flash

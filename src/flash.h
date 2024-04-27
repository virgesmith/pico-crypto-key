#pragma once

#include "utils.h"

#include <hardware/flash.h>
#include <hardware/sync.h> // for interrupts

namespace flash {
// returns 0 if subsequent read matches whats requested to be written
// (so will be nonzero if b is longer than sector size and truncated)
uint32_t write(const bytes& b);
bytes read(size_t length);
} // namespace flash

#pragma once

#include "pico/stdlib.h"

struct ErrorCode
{
  enum Value {
    PIN = 2*8, EC = 3*8, AES = 4*8,
    INVALID_KEYPAIR = 1, INVALID_KEY_LENGTH = 2, MEMORY = 3, FEATURE = 4, UNKNOWN = 7
  };
};

void error_state(int e);

#include "error.h"
#include "board.h"

#include "pico/stdlib.h"

#include <algorithm>


void ErrorMapper::check(int ret) {
  if (ret == 0)
    return;
  auto it = std::find(states.begin(), states.end(), ret);
  enter(it == states.end() ? 0 : it - states.begin() + 1);
}

void ErrorMapper::enter(int code) {
  for (;;) {
    board::error(context, code);
  }
}

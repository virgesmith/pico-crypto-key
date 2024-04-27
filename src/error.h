#pragma once

#include <vector>

struct ErrorMapper final
{
  enum Context
  {
    EC = 1, AES = 2, SHA = 3
  };

  // individual error states. Do not provide more than 7 states!
  ErrorMapper(Context c, std::vector<int>&& s) : context(c), states(s) {}

  void check(int ret);

  void enter(int code);

  Context context;
  std::vector<int> states;
};

//void error_state(int e);

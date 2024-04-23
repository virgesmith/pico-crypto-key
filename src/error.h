#pragma once

#include <vector>

struct ErrorMapper final
{
  enum Context
  {
    PIN = 2, EC = 3, AES = 4, SHA = 5
  };

  // individual error states. Do not provide more than 7 states!
  ErrorMapper(Context c, std::vector<int>&& s) : context(c), states(s) {}

  void check(int ret);

  void enter(int code);

  Context context;
  std::vector<int> states;
};

//void error_state(int e);

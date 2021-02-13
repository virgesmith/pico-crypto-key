cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(test_crypto)
pico_sdk_init()
add_executable(test
  main.cpp
  sha256.cpp
)
pico_enable_stdio_usb(test 1)
pico_add_extra_outputs(test)
target_compile_options(test PRIVATE -Wno-psabi)
target_link_libraries(test pico_stdlib pico_unique_id)
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -std=c++17")
cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(crypto)
pico_sdk_init()
add_executable(crypto
  main.cpp
  base64.cpp
  sha256.cpp
)
pico_enable_stdio_usb(crypto 1)
pico_enable_stdio_uart(crypto 0)
pico_add_extra_outputs(crypto)
target_compile_options(crypto PRIVATE -Wno-psabi)
target_link_libraries(crypto pico_stdlib pico_unique_id)
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -std=c++17")
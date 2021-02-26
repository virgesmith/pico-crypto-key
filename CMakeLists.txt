cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(crypto)
pico_sdk_init()
add_executable(crypto
  src/main.cpp
  src/utils.cpp
  src/serial.cpp
  src/sha256.cpp
  src/ecdsa.cpp
  src/aes.cpp
)
add_subdirectory(mbedtls-2.25.0 EXCLUDE_FROM_ALL)
pico_enable_stdio_usb(crypto 1)
pico_enable_stdio_uart(crypto 0)
pico_add_extra_outputs(crypto)
include_directories(${CMAKE_SOURCE_DIR}/mbedtls-2.25.0/include)
target_compile_options(crypto PRIVATE -Wno-psabi -Werror -Wall)
target_link_libraries(crypto pico_stdlib pico_unique_id mbedcrypto)
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -std=c++17")
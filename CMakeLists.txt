
cmake_minimum_required(VERSION 3.13)

message("Target is ${PICO_IMAGE}")
include(pico_sdk_import.cmake)
project(crypto)
pico_sdk_init()
add_executable(${PICO_IMAGE}
  src/main.cpp
  src/utils.cpp
  src/serial.cpp
  src/sha256.cpp
  src/ecdsa.cpp
  src/aes.cpp
  src/device.cpp
  src/error.cpp
)

add_subdirectory(mbedtls EXCLUDE_FROM_ALL)
pico_enable_stdio_usb(${PICO_IMAGE} 1)
pico_enable_stdio_uart(${PICO_IMAGE} 0)
pico_add_extra_outputs(${PICO_IMAGE})
include_directories(${CMAKE_SOURCE_DIR}/mbedtls/include)
target_compile_options(${PICO_IMAGE} PRIVATE -Wno-psabi -Werror -Wall -DMBEDTLS_ALLOW_PRIVATE_ACCESS)
# warning disabled due to this: pico-sdk/lib/tinyusb/src/portable/raspberrypi/rp2040/rp2040_usb.h:139
target_link_libraries(${PICO_IMAGE} pico_stdlib pico_unique_id mbedcrypto)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20")
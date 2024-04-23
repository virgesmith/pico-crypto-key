
cmake_minimum_required(VERSION 3.13)

message("Target is ${PICO_IMAGE}")
include(pico_sdk_import.cmake)

project(crypto)
set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)
pico_sdk_init()

add_executable(${PICO_IMAGE}
  src/main.cpp
  src/usb_cdc.cpp
  src/sha256.cpp
  src/ecdsa.cpp
  src/aes.cpp
  src/device.cpp
  src/flash.cpp
  src/error.cpp
  src/usb_descriptors.c
)

add_subdirectory(mbedtls EXCLUDE_FROM_ALL)
pico_add_extra_outputs(${PICO_IMAGE})

target_include_directories(${PICO_IMAGE} PUBLIC ${CMAKE_CURRENT_LIST_DIR}/src ${CMAKE_CURRENT_LIST_DIR}/mbedtls/include)

# include_directories(${CMAKE_SOURCE_DIR}/mbedtls/include)
target_compile_options(${PICO_IMAGE} PRIVATE -Wno-psabi -Werror -Wall -DMBEDTLS_ALLOW_PRIVATE_ACCESS)
# warning disabled due to this: pico-sdk/lib/tinyusb/src/portable/raspberrypi/rp2040/rp2040_usb.h:139
target_link_libraries(${PICO_IMAGE}
  pico_stdlib
  pico_unique_id
  hardware_flash
  hardware_sync
  tinyusb_device
  tinyusb_board
  mbedcrypto
)

message("Target is ${PICO_RESET_PIN}")

add_executable(${PICO_RESET_PIN}
  src/reset_pin.cpp
  src/flash.cpp
)

target_compile_options(${PICO_RESET_PIN} PRIVATE -Wno-psabi -Werror -Wall -DMBEDTLS_ALLOW_PRIVATE_ACCESS)
target_link_libraries(${PICO_RESET_PIN}
  pico_stdlib
  hardware_flash
  hardware_sync
)
pico_add_extra_outputs(${PICO_RESET_PIN})


cmake_minimum_required(VERSION 3.13)

message("Board is ${PICO_BOARD}")
set(PICO_IMAGE "crypto-key")
set(PICO_RESET_PIN "reset-pin")
set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)

include(pico_sdk_import.cmake)

project(crypto)

pico_sdk_init()

message("Target is ${PICO_IMAGE}")

add_executable(${PICO_IMAGE}
  src/main.cpp
  src/usb_cdc.cpp
  src/sha256.cpp
  src/ecdsa.cpp
  src/aes.cpp
  src/flash.cpp
  src/board.cpp
  src/error.cpp
  src/pin.cpp
  src/usb_descriptors.c
)

add_subdirectory(mbedtls EXCLUDE_FROM_ALL)

target_compile_definitions(${PICO_IMAGE} PUBLIC BOARD_${PICO_BOARD} PCK_VER=${PCK_VER})
target_include_directories(${PICO_IMAGE} PUBLIC ${CMAKE_CURRENT_LIST_DIR}/src ${CMAKE_CURRENT_LIST_DIR}/mbedtls/include)
target_compile_options(${PICO_IMAGE} PRIVATE -Wno-psabi -Werror -Wall -DMBEDTLS_ALLOW_PRIVATE_ACCESS)
# warning disabled due to this: pico-sdk/lib/tinyusb/src/portable/raspberrypi/rp2040/rp2040_usb.h:139

if(${PICO_BOARD} STREQUAL pico_w)
  target_link_libraries(${PICO_IMAGE}
    pico_stdlib
    pico_unique_id
    hardware_flash
    hardware_sync
    tinyusb_device
    tinyusb_board
    mbedcrypto
    pico_cyw43_arch_none
  )
elseif(${PICO_BOARD} STREQUAL pico2)
  target_link_libraries(${PICO_IMAGE}
    pico_stdlib
    pico_unique_id
    pico_sha256
    hardware_flash
    hardware_sync
    tinyusb_device
    tinyusb_board
    mbedcrypto
  )
else()
  target_link_libraries(${PICO_IMAGE}
    pico_stdlib
    pico_unique_id
    hardware_flash
    hardware_sync
    tinyusb_device
    tinyusb_board
    mbedcrypto
  )
endif()

pico_set_program_name(${PICO_IMAGE} "PicoCryptoKey")
pico_set_program_version(${PICO_IMAGE} ${PCK_VER})

pico_add_extra_outputs(${PICO_IMAGE})

message("Target is ${PICO_RESET_PIN}")

add_executable(${PICO_RESET_PIN}
  src/reset_pin.cpp
  src/flash.cpp
  src/board.cpp
  src/error.cpp
)

target_compile_definitions(${PICO_RESET_PIN} PRIVATE BOARD_${PICO_BOARD})
target_compile_options(${PICO_RESET_PIN} PRIVATE -Wno-psabi -Werror -Wall)

if(${PICO_BOARD} STREQUAL pico_w)
  target_link_libraries(${PICO_RESET_PIN}
    pico_stdlib
    hardware_flash
    hardware_sync
    pico_cyw43_arch_none
  )
else()
  target_link_libraries(${PICO_RESET_PIN}
    pico_stdlib
    hardware_flash
    hardware_sync
  )
endif()

pico_set_program_name(${PICO_RESET_PIN} "PicoCryptoKeyPinReset")
pico_set_program_version(${PICO_RESET_PIN} ${PCK_VER})

pico_add_extra_outputs(${PICO_RESET_PIN})

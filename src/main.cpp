#include "aes.h"
#include "device.h"
#include "ecdsa.h"
#include "error.h"
#include "flash.h"
#include "sha256.h"
#include "usb_cdc.h"
#include "utils.h"

#include "pico/binary_info.h"
#include "pico/unique_id.h"

#include <string>
#include <vector>

enum class ErrorCode : uint32_t { SUCCESS = 0, INVALID_PIN = 1, INVALID_CMD = 2 };

// raw private key for AES and ECDSA
bytes genkey() {
  // 8 byte salt + 8 byte board id -> sha256
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);
  bytes raw{0xaa, 0xfe, 0xc0, 0xff, 0xba, 0xda, 0x55, 0x55};
  raw.insert(raw.end(), id.id, id.id + PICO_UNIQUE_BOARD_ID_SIZE_BYTES);

  return sha256::hash(raw);
}

namespace {
  const bytes salt = {0x19, 0x93, 0x76, 0x02, 0x45, 0x4a, 0xbc, 0xde};
}

bool check_pin() {
  bytes expected = flash::read(32);
  uint32_t size;
  cdc::read(size);
  bytes pin(size);
  cdc::read(pin);
  pin.reserve(pin.size() + 8);
  pin.insert(pin.end(), salt.begin(), salt.end());
  bytes h = sha256::hash(pin);
  return h == expected;
}

uint32_t set_pin() {
  uint32_t size;
  cdc::read(size);
  bytes pin(size);
  cdc::read(pin);
  pin.reserve(pin.size() + 8);
  pin.insert(pin.end(), salt.begin(), salt.end());
  bytes h = sha256::hash(pin);
  flash::write(h);
  return 0;
}

void repl(const mbedtls_ecp_keypair& ec_key, const mbedtls_aes_context& aes_key) {
  uint8_t cmd;
  for (;;) {
    cdc::read(cmd);
    switch (cmd) {
    // reset repl
    case 'r': {
      return;
    }
    // write pin
    case 'p': {
      gpio_put(LED_PIN, 1);
      cdc::write(set_pin());
      gpio_put(LED_PIN, 0);
      break;
    }
    // read pin
    case 'X': {
      gpio_put(LED_PIN, 1);
      bytes b = flash::read(32);
      cdc::write(b);
      gpio_put(LED_PIN, 0);
      break;
    }
    // get ECDSA public key
    case 'k': {
      gpio_put(LED_PIN, 1);
      cdc::write(ecdsa::pubkey(ec_key));
      gpio_put(LED_PIN, 0);
      break;
    }
    // hash input
    case 'h': {
      // 4 byte header containing length of data
      gpio_put(LED_PIN, 1);
      uint32_t length;
      cdc::read(length);
      bytes hash = sha256::hash_in(length);
      cdc::write(hash);
      gpio_put(LED_PIN, 0);
      break;
    }
    // decrypt input
    case 'd': {
      // 4 byte header containing length of data
      gpio_put(LED_PIN, 1);
      uint32_t length;
      cdc::read(length);
      aes::decrypt_in(aes_key, length);
      gpio_put(LED_PIN, 0);
      break;
    }
    // encrypt input
    case 'e': {
      // 4 byte header containing length of data
      gpio_put(LED_PIN, 1);
      uint32_t length;
      cdc::read(length);
      aes::encrypt_in(aes_key, length);
      gpio_put(LED_PIN, 0);
      break;
    }
    // hash input and sign
    case 's': {
      // 4 byte header containing length of data
      gpio_put(LED_PIN, 1);
      uint32_t length;
      cdc::read(length);
      bytes hash = sha256::hash_in(length);
      cdc::write(hash);
      bytes sig = ecdsa::sign(ec_key, hash);
      cdc::write(sig.size());
      cdc::write(sig);
      gpio_put(LED_PIN, 0);
      break;
    }
    // verify hash and signature
    case 'v': {
      // hash[32], len(sig)[4], sig, len(key)[4], key
      gpio_put(LED_PIN, 1);
      uint32_t length;
      bytes hash(sha256::LENGTH_BYTES);
      cdc::read(hash);
      // read signature
      cdc::read(length);
      bytes sig(length);
      cdc::read(sig);
      // read pubkey
      cdc::read(length);
      bytes pubkey(length);
      cdc::read(pubkey);
      // 4-byte int, 0 is success
      cdc::write(ecdsa::verify(hash, sig, pubkey));
      gpio_put(LED_PIN, 0);
      break;
    }
    default: {
      cdc::write(ErrorCode::INVALID_CMD);
    }
    }
  }
}

int main() {
  bi_decl(bi_program_description("PicoCryptoKey"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  tusb_init();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);
  gpio_put(LED_PIN, 1);
  sleep_ms(100);
  gpio_put(LED_PIN, 0);

  for (;;) {
    while (!check_pin()) {
      gpio_put(LED_PIN, 0);
      cdc::write(ErrorCode::INVALID_PIN);

      sleep_ms(3000);
    }
    cdc::write(ErrorCode::SUCCESS);

    const bytes& key = genkey();

    wrap<mbedtls_ecp_keypair> ec_key(mbedtls_ecp_keypair_init, mbedtls_ecp_keypair_free);
    ecdsa::key(key, *ec_key);

    wrap<mbedtls_aes_context> aes_key(mbedtls_aes_init, mbedtls_aes_free);
    aes::key(key, *aes_key);

    // accept commands until reset
    repl(*ec_key, *aes_key);

    sleep_ms(250);
  }
}

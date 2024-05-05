#include "aes.h"
#include "board.h"
#include "ecdsa.h"
#include "error.h"
#include "pin.h"
#include "sha256.h"
#include "usb_cdc.h"
#include "utils.h"

#include "pico/binary_info.h"
#include "pico/stdlib.h"
#include "pico/unique_id.h"

#include <string>
#include <vector>

#define STR(s) STR_IMPL(s)
#define STR_IMPL(s) #s

const std::string VER(STR(PCK_VER) "-" PICO_BOARD);

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

void append_timestamp(bytes& challenge) {
  uint64_t timestamp = get_time_ms();
  timestamp = timestamp - timestamp % AUTH_TIME_VALIDITY_MS;
  byte* p = reinterpret_cast<byte*>(&timestamp);
  // this is little-endian
  challenge.reserve(challenge.size() + sizeof(timestamp));
  challenge.insert(challenge.end(), p, p + sizeof(timestamp));
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
      led::on();
      cdc::write(pin::set());
      led::off();
      break;
    }
    // get ECDSA public key
    case 'k': {
      led::on();
      cdc::write(ecdsa::pubkey(ec_key));
      led::off();
      break;
    }
    // hash input
    case 'h': {
      led::on();
      bytes hash = sha256::hash_in();
      cdc::write(hash);
      led::off();
      break;
    }
    // decrypt input
    case 'd': {
      led::on();
      aes::decrypt_in(aes_key);
      led::off();
      break;
    }
    // encrypt input
    case 'e': {
      led::on();
      aes::encrypt_in(aes_key);
      led::off();
      break;
    }
    // hash input and sign
    case 's': {
      led::on();
      bytes hash = sha256::hash_in();
      cdc::write(hash);
      bytes sig = ecdsa::sign(ec_key, hash);
      cdc::write_with_length(sig);
      led::off();
      break;
    }
    // verify hash and signature
    case 'v': {
      // hash[32], len(sig)[4], sig, len(key)[4], key
      led::on();
      bytes hash(sha256::LENGTH_BYTES);
      cdc::read(hash);
      bytes sig = cdc::read_with_length();
      bytes pubkey = cdc::read_with_length();
      // 4-byte int, 0 is success
      cdc::write(ecdsa::verify(hash, sig, pubkey));
      led::off();
      break;
    }
    // authenticate: read challenge bytes, append timestamp, hash, sign
    case 'a': {
      led::on();
      bytes challenge = cdc::read_with_length();
      // append timestamp bytes
      append_timestamp(challenge);
      // hash and sign
      bytes hash = sha256::hash(challenge);
      bytes sig = ecdsa::sign(ec_key, hash);
      // write signature
      cdc::write_with_length(sig);
      led::off();
      break;
    }
    // board info
    case 'i': {
      led::on();
      cdc::write(VER.size() + sizeof(uint64_t));
      cdc::write(VER);
      cdc::write(get_time_ms());
      led::off();
      break;
    }
    default: {
      cdc::write(ErrorCode::INVALID_CMD);
    }
    }
  }
}

int main() {
  bi_decl(bi_program_name("PicoCryptoKey"));

  tusb_init();
  led::init();

  for (;;) {
    while (!pin::check()) {
      led::off();
      cdc::write(ErrorCode::INVALID_PIN);

      sleep_ms(3000);
    }
    cdc::write(ErrorCode::SUCCESS);
    // host will send timestamp on success
    uint64_t timestamp_ms;
    cdc::read(timestamp_ms);
    set_time_offset(timestamp_ms);

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

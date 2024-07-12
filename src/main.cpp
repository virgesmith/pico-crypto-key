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
// Omit extra for "master" key
bytes genkey(const bytes& extra = bytes()) {
  // 8 byte salt + 8 byte board id -> sha256
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);
  bytes raw{0xaa, 0xfe, 0xc0, 0xff, 0xba, 0xda, 0x55, 0x55};
  raw.reserve(raw.size() + PICO_UNIQUE_BOARD_ID_SIZE_BYTES + extra.size());
  raw.insert(raw.end(), id.id, id.id + PICO_UNIQUE_BOARD_ID_SIZE_BYTES);
  raw.insert(raw.end(), extra.begin(), extra.end());

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
    board::ready();
    cdc::read(cmd);
    board::busy();
    switch (cmd) {
    // reset repl
    case 'x': {
      board::clear();
      return;
    }
    // write pin
    case 'p': {
      cdc::write(pin::set());
      break;
    }
    // get ECDSA public key
    case 'k': {
      cdc::write(ecdsa::pubkey(ec_key));
      break;
    }
    // hash input
    case 'h': {
      bytes hash = sha256::hash_in();
      cdc::write(hash);
      break;
    }
    // decrypt input
    case 'd': {
      aes::decrypt_in(aes_key);
      break;
    }
    // encrypt input
    case 'e': {
      aes::encrypt_in(aes_key);
      break;
    }
    // hash input and sign
    case 's': {
      bytes hash = sha256::hash_in();
      cdc::write(hash);
      bytes sig = ecdsa::sign(ec_key, hash);
      cdc::write_with_length(sig);
      break;
    }
    // verify hash and signature
    case 'v': {
      // hash[32], len(sig)[4], sig, len(key)[4], key
      bytes hash(sha256::LENGTH_BYTES);
      cdc::read(hash);
      bytes sig = cdc::read_with_length();
      bytes pubkey = cdc::read_with_length();
      // 4-byte int, 0 is success
      cdc::write(ecdsa::verify(hash, sig, pubkey));
      break;
    }
    // webauthn register: generate keypair from user and relying party ids, return public key
    case 'r': {
      bytes rp = cdc::read_with_length();
      wrap<mbedtls_ecp_keypair> webauthn_key(mbedtls_ecp_keypair_init, mbedtls_ecp_keypair_free);
      ecdsa::key(genkey(rp), *webauthn_key);
      cdc::write(ecdsa::pubkey(*webauthn_key));
      break;
    }
    // webauthn authenticate: read id, generate keypair, read challenge bytes, append timestamp, hash, sign
    case 'a': {
      // generate keypair
      bytes rp = cdc::read_with_length();
      wrap<mbedtls_ecp_keypair> webauthn_key(mbedtls_ecp_keypair_init, mbedtls_ecp_keypair_free);
      ecdsa::key(genkey(rp), *webauthn_key);
      bytes challenge = cdc::read_with_length();
      // append timestamp bytes
      append_timestamp(challenge);
      // hash and sign
      bytes hash = sha256::hash(challenge);
      bytes sig = ecdsa::sign(*webauthn_key, hash);
      // write signature
      cdc::write_with_length(sig);
      break;
    }
    // board info
    case 'i': {
      cdc::write(VER.size() + sizeof(uint64_t));
      cdc::write(VER);
      cdc::write(get_time_ms());
      break;
    }
    default: {
      board::invalid();
      cdc::write(ErrorCode::INVALID_CMD);
      sleep_ms(500);
    }
    }
  }
}

int main() {
  bi_decl(bi_program_name("PicoCryptoKey"));

  tusb_init();
  board::init();

  for (;;) {
    while (!pin::check()) {
      cdc::write(ErrorCode::INVALID_PIN);

      board::invalid();
      sleep_ms(3000);
      board::clear();
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

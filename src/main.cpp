#include "sha256.h"
#include "aes.h"
#include "ecdsa.h"
#include "usb_cdc.h"
#include "utils.h"
#include "device.h"
#include "error.h"

//#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

const char* help_str = R"(The device must first be supplied with a correct pin to enter the repl
repl commands:
H displays this message
h computes sha256 hash of data streamed to device
  inputs: <data> <data> <data>... <>
  returns: <hash>
k get the public key
  inputs: none
  returns: <pubkey>
d decrypts each chunk of streamed data
  inputs: <data> <data>... <>
  returns: <data> <data>...
e encrypts each chunk of streamed data
  inputs: <data> <data>... <>
  returns: <data> <data>...
s hashes and signs (the hash of) the streamed data
  inputs: <data> <data>... <>
  returns: <hash> <sig>
v verifies a signature
  inputs: <hash> <sig> <pubkey>
  returns: stringified integer. 0 if verification was successful
r resets the device repl (i.e. pin will need to be reentered)
  inputs: none
  returns: nothing
All commands are a single character (no newline).
All data sent and received is base64 encoded and terminated with a newline,
unless otherwise specified. Where a variable number of inputs is received,
a blank line is used to indicate the end of the data.

)";


// raw private key for AES and ECDSA
bytes genkey()
{
  // 8 byte salt + 8 byte board id -> sha256
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);
  bytes raw{ 0xaa, 0xfe, 0xc0, 0xff, 0xba, 0xda, 0x55, 0x55 };
  raw.insert(raw.end(), id.id, id.id + PICO_UNIQUE_BOARD_ID_SIZE_BYTES);

  return sha256::hash(raw);
}

bool check_pin()
{
  static const bytes expected{27, 122, 143, 3, 174, 184, 22, 106, 189, 29, 77, 163, 101, 226, 4, 61, 171,
                  209, 237, 213, 208, 154, 177, 121, 108, 235, 5, 150, 29, 117, 204, 222};
  static const bytes salt = { 0x19, 0x93, 0x76, 0x02, 0x45, 0x4a, 0xbc, 0xde };
  bytes pin(4);
  cdc::read(pin, pin.size());
  pin.insert(pin.end(), salt.begin(), salt.end());
  bytes h = sha256::hash(pin);
  return h == expected;
}

void repl(const mbedtls_ecp_keypair& ec_key, const mbedtls_aes_context& aes_key)
{
  // 'r' resets repl (pin needs to be reentered)
  // for (char cmd = getchar(); cmd != 'r'; cmd = getchar())
  uint8_t cmd;
  for(;;)
  {
    cdc::read(cmd);
    switch (cmd)
    {
      case 'r':
      {
        // resets repl
        return;
      }
      case 'H':
      {
        gpio_put(LED_PIN, 1);
        cdc::write(help_str);
        gpio_put(LED_PIN, 0);
        break;
      }
      case 'k':
      {
        gpio_put(LED_PIN, 1);
        cdc::write(ecdsa::pubkey(ec_key));
        gpio_put(LED_PIN, 0);
        break;
      }
      case 'h':
      {
        // 4 byte header containing length of data
        gpio_put(LED_PIN, 1);
        uint32_t length;
        cdc::read(length);
        bytes hash = sha256::hash_in(length);
        cdc::write(hash);
        gpio_put(LED_PIN, 0);
        break;
      }
      case 'd':
      {
        // 4 byte header containing length of data
        gpio_put(LED_PIN, 1);
        uint32_t length;
        cdc::read(length);
        aes::decrypt_in(aes_key, length);
        gpio_put(LED_PIN, 0);
        break;
      }
      case 'e':
      {
        // 4 byte header containing length of data
        gpio_put(LED_PIN, 1);
        uint32_t length;
        cdc::read(length);
        aes::encrypt_in(aes_key, length);
        gpio_put(LED_PIN, 0);
        break;
      }
      case 's':
      {
        // 4 byte header containing length of data
        gpio_put(LED_PIN, 1);
        uint32_t length;
        cdc::read(length);
        bytes hash = sha256::hash_in(length);
        cdc::write(hash);
        bytes sig = ecdsa::sign(ec_key, hash);
        if (sig.empty())
          cdc::write("ERROR in ecdsa::sign");
        else
          cdc::write(sig);
        gpio_put(LED_PIN, 0);
        break;
      }
      case 'v':
      {
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
      default:
      {
        cdc::write("%% not a valid command"s % cmd);
      }
    }
    //sleep_ms(250);
  }
}


int main()
{
  bi_decl(bi_program_description("PicoCryptoKey"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  tusb_init();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);
  gpio_put(LED_PIN, 1);
  sleep_ms(100);
  gpio_put(LED_PIN, 0);

  for(;;)
  {
    while (!check_pin())
    {
      gpio_put(LED_PIN, 0);
      cdc::write("pin err");

      sleep_ms(3000);
    }
    cdc::write("pin ok");

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

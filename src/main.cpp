#include "sha256.h"
#include "aes.h"
#include "ecdsa.h"
#include "serial.h"
#include "utils.h"

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

const char* help_str = R"(Usage:
commands:

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

r resets the device repl (pin needs to be reentered)
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
  const std::string& pinstr(serial::recv());
  bytes pin{pinstr.begin(), pinstr.end()};
  pin.insert(pin.end(), salt.begin(), salt.end());
  bytes h = sha256::hash(pin);

  return h == expected;
}

void repl(const mbedtls_ecp_keypair& ec_key, const mbedtls_aes_context& aes_key)
{
  // 'r' resets repl (pin needs to be reentered)
  for (char cmd = std::getchar(); cmd != 'r'; cmd = std::getchar())
  {
    switch (cmd)
    {
      // case 'D':
      // {
      //   if (check_pin())
      //     serial::send("pin ok\n");
      //   else
      //     serial::send("pin error\n");
      //   break;
      // }
      case 'H':
      {
        serial::send(help_str);
        break;
      }
      case 'k':
      {
        const bytes& pubkey = ecdsa::pubkey(ec_key);
        if (pubkey.empty())
          serial::send("ERROR in ecdsa::pubkey\n");
        else
          serial::send(base64::encode(pubkey) + "\n");
        break;
      }
      case 'h':
      {
        serial::send(base64::encode(sha256::hash_stdin()) + "\n");
        break;
      }
      case 'd':
      {
        aes::decrypt_stdin(aes_key);
        break;
      }
      case 'e':
      {
        aes::encrypt_stdin(aes_key);
        break;
      }
      case 's':
      {
        bytes h = sha256::hash_stdin();
        serial::send(base64::encode(h) + "\n");
        bytes sig = ecdsa::sign(ec_key, h);
        if (sig.empty())
          serial::send("ERROR in ecdsa::sign\n");
        serial::send(base64::encode(sig) + "\n");
        break;
      }
      case 'v':
      {
        bytes hash = base64::decode(serial::recv());
        bytes sig = base64::decode(serial::recv());
        bytes pubkey = base64::decode(serial::recv());
        serial::send("%%\n"s % ecdsa::verify(hash, sig, pubkey));
        break;
      }
      default:
      {
        serial::send("%% not a valid command"s % cmd);
      }
    }
    //sleep_ms(250);
  }
}


int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  for(;;)
  {

    while (!check_pin())
    {
      sleep_ms(3000);
      serial::send("incorrect pin\n");
    }
    serial::send("pin ok\n");

    const bytes& key = genkey();

    // not wrapped as never freed
    const mbedtls_ecp_keypair& ec_key = ecdsa::key(key);
    const mbedtls_aes_context& aes_key = aes::key(key);

    // accept comands until reset
    repl(ec_key,aes_key);
  }
}
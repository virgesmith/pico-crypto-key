#include "base64.h"
#include "sha256.h"
#include "aes.h"
#include "serial.h"

#include "mbedtls/ecp.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/pk.h"

#include "mbedtls/asn1write.h" // for local ecdsa_signature_to_asn1
#include "mbedtls/error.h" // for local ecdsa_signature_to_asn1

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/binary_info.h"

#include <vector>
#include <string>

#include <cstring> // for memcpy

namespace {

// copied from ecdsa.c (where its static)
extern "C" int ecdsa_signature_to_asn1( const mbedtls_mpi *r, const mbedtls_mpi *s,
                                    unsigned char *sig, size_t *slen )
{
    int ret = MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED;
    unsigned char buf[MBEDTLS_ECDSA_MAX_LEN];
    unsigned char *p = buf + sizeof( buf );
    size_t len = 0;

    MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_mpi( &p, buf, s ) );
    MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_mpi( &p, buf, r ) );

    MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_len( &p, buf, len ) );
    MBEDTLS_ASN1_CHK_ADD( len, mbedtls_asn1_write_tag( &p, buf,
                                       MBEDTLS_ASN1_CONSTRUCTED | MBEDTLS_ASN1_SEQUENCE ) );

    memcpy( sig, p, len );
    *slen = len;

    return( 0 );
}

//int (*f_rng_blind)(void *, unsigned char *, size_t)
extern "C" int minstd_rand(void*, byte* p, size_t n)
{
  static uint32_t r = 1;
  for (size_t i = 0; i < n; ++i)
  {
    r = r * 48271 % 2147483647;
    p[i] = static_cast<byte>(r); // % 256;
  }
  return 0;
}

}

namespace std
{

// prevents char being casted to int
std::string to_string(char c)
{
  return std::string(1, c);
}

}

template<typename T>
std::string operator%(std::string&& str, T value)
{
  size_t s = str.find("%%");
  if (s != std::string::npos)
  {
    str.replace(s, 2, std::to_string(value));
  }
  return std::move(str);
}

using namespace std::string_literals;


bytes hash_impl()
{
  SHA256_CTX ctx;
  sha256_init(&ctx);
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes s = base64::decode(chunk);
    sha256_update(&ctx, (byte*)&*s.cbegin(), s.size());
  }
  bytes h(SHA256_BLOCK_SIZE);
  sha256_final(&ctx, h.data());
  return h;
}

void hash()
{
  serial::send(base64::encode(hash_impl()) + "\n");
}

void sign(const mbedtls_ecp_keypair& key)
{
  bytes h = hash_impl();
  serial::send(base64::encode(h) + "\n");

  mbedtls_mpi r, s;
  mbedtls_mpi_init(&r);
  mbedtls_mpi_init(&s);

  int ret = mbedtls_ecdsa_sign_det_ext(const_cast<mbedtls_ecp_group*>(&key.grp) /* ? */, &r, &s, &key.d,
                              h.data(), h.size(), MBEDTLS_MD_SHA256,
                              minstd_rand, NULL);

  bytes sig(MBEDTLS_ECDSA_MAX_LEN);
  size_t sz = 0;
  ecdsa_signature_to_asn1(&r, &s, sig.data(), &sz);
  // trim
  sig.resize(sz);

  serial::send(base64::encode(sig) + "\n");
}


void verify()
{
  bytes hash = base64::decode(serial::recv());
  bytes sig = base64::decode(serial::recv());
  bytes pubkey = base64::decode(serial::recv());

  mbedtls_ecdsa_context ec_key; // context is keypair typedef. needs to be initialised with group and pubkey
  mbedtls_ecdsa_init(&ec_key);
  int ret = mbedtls_ecp_group_load(&ec_key.grp, MBEDTLS_ECP_DP_SECP256K1);
  if (ret)
  {
    serial::send("mbedtls_ecp_group_load error %%\n"s % ret);
    return;
  }
  ret = mbedtls_ecp_point_read_binary(&ec_key.grp, &ec_key.Q, pubkey.data(), pubkey.size());
  if (ret)
  {
    serial::send("mbedtls_ecp_point_read_binary error %%\n"s % ret);
    return;
  }

  ret = mbedtls_ecdsa_read_signature(&ec_key, hash.data(), hash.size(), sig.data(), sig.size());
  serial::send("%%\n"s % ret);
}

void decrypt(const std::vector<uint32_t>& key)
{
  bytes iv{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes c = base64::decode(chunk);
    bytes p(c.size());

    aes_decrypt_ctr(c.data(), c.size(), p.data(), key.data(), 256, iv.data());
    // TODO call increment_iv?

    serial::send(base64::encode(p) + "\n");
  }
}

void encrypt(const std::vector<uint32_t>& key)
{
  bytes iv{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  for(std::string chunk = serial::recv(); !chunk.empty(); chunk = serial::recv())
  {
    bytes p = base64::decode(chunk);
    bytes c(p.size());

    aes_encrypt_ctr(p.data(), p.size(), c.data(), key.data(), 256, iv.data());
    // TODO call increment_iv?

    serial::send(base64::encode(c) + "\n");
  }
}

// private key for AES and ECDSA
bytes genkey()
{
  // 8 byte salt + 8 byte board id -> sha256
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);
  bytes raw{ 0xaa, 0xfe, 0xc0, 0xff, 0xba, 0xda, 0x55, 0x55 };
  raw.insert(raw.end(), id.id, id.id + PICO_UNIQUE_BOARD_ID_SIZE_BYTES);

  SHA256_CTX ctx;
  sha256_init(&ctx);
  sha256_update(&ctx, raw.data(), raw.size());
  bytes key(SHA256_BLOCK_SIZE);
  sha256_final(&ctx, key.data());
  return key;
}

// verify (specifically mbedtls_ecp_point_read_binary) only supports uncompressed keys
void pubkey(const mbedtls_ecp_keypair& ec_key)
{
  bytes pubkey(65);
  size_t outlen;

  int ret = mbedtls_ecp_check_pub_priv(&ec_key, &ec_key);
  if (ret != 0)
  {
    serial::send("ERROR in mbedtls_ecp_check_pub_priv: %%\n"s % ret);
    return;
  }

  ret = mbedtls_ecp_point_write_binary(&ec_key.grp,
                                 &ec_key.Q,
                                 MBEDTLS_ECP_PF_UNCOMPRESSED,
                                 &outlen,
                                 pubkey.data(),
                                 pubkey.size());
  if (ret != 0)
    serial::send("ERROR in mbedtls_ecp_point_write_binary\n");
  else
    serial::send(base64::encode(pubkey) + "\n");
}

int main()
{
  bi_decl(bi_program_description("Crypto key"));
  bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

  stdio_init_all();
  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  const bytes& key = genkey();

  mbedtls_ecdsa_context ec_ctx;
  mbedtls_ecdsa_init(&ec_ctx);
  mbedtls_ecp_keypair ec_key;
  mbedtls_ecp_keypair_init(&ec_key);
  int ret = mbedtls_ecp_read_key(MBEDTLS_ECP_DP_SECP256K1, &ec_key, key.data(), key.size());
  ret = mbedtls_ecp_mul(&ec_key.grp, &ec_key.Q, &ec_key.d, &ec_key.grp.G, NULL, NULL);

  std::vector<uint32_t> key_schedule(60);
  aes_key_setup(key.data(), key_schedule.data(), SHA256_BLOCK_SIZE*8);

  for (char cmd = std::getchar(); true; cmd = std::getchar())
  {
    switch (cmd)
    {
      case 'D':
      {
        serial::send("DBG: mbedtls_ecp_mul ret=%%\n"s % ret);
        serial::send("DBG: key=" + base64::encode(key) + "\n");
        serial::send("DBG: ec ok=%%\n"s % (mbedtls_ecp_check_pub_priv(&ec_key, &ec_key) == 0));
        break;
      }
      case 'H':
      {
        serial::send("help: TODO"s);
        break;
      }
      case 'k':
      {
        pubkey(ec_key);
        break;
      }
      case 'h':
      {
        hash();
        break;
      }
      case 'd':
      {
        decrypt(key_schedule);
        break;
      }
      case 'e':
      {
        encrypt(key_schedule);
        break;
      }
      case 's':
      {
        sign(ec_key);
        break;
      }
      case 'v':
      {
        verify();
        break;
      }
      default:
      {
        serial::send("%% not a valid command"s % cmd);
      }
    }
    sleep_ms(250);
  }
}
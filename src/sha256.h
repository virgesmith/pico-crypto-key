
#include "utils.h"

namespace sha256
{

const size_t LENGTH_BYTES = 32;
const size_t LENGTH_BITS = 256;

bytes hash(const bytes& data);

// hashes base64-encoded stdin until a blank line is read
bytes hash_stdin();

}
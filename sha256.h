
#include "utils.h"
#include "sha256_bcon.h"

namespace sha256
{

bytes hash(const bytes& data);

// hashes stdin until a blank line is read
bytes hash_stdin();

}

#include "utils.h"

namespace sha256 {

const size_t LENGTH_BYTES = 32;

bytes hash(const bytes& data);

// hashes CDC input
bytes hash_in(uint32_t length);

} // namespace sha256
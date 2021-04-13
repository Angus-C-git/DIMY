# ============================= Imports ============================= #
import pyhash
from bitarray import bitarray

# =========================== Middlewares ============================ #

BLOOM_SIZE = 800000  # 100KB
HASH_ROUNDS = 3  # Compute 3 hashes for each entry
fnv_hash = pyhash.fnv1_32()
murmur_hash = pyhash.murmur3_32()

DEVICE_DBFS = []
# ============================ Functions ============================ #

# TODO: Some kind of function handled by a runner thread
'''
Uses timing module to keep track of how long a DBF has been alive for.
Manages the global queue of DBFs popping entries which have a age equal
to 6 (representing a DBF older than 60 minutes).
'''


def compute_hash_indexes(entry):
    print("[>>] Computing 3 rounds of murmur hash")
    indexes = []
    prev_hash = entry
    for cr in range(0, HASH_ROUNDS):
        indexes.append(murmur_hash(prev_hash) % BLOOM_SIZE)
        prev_hash = str(murmur_hash(prev_hash))

    return indexes


# ========================== Bloom Classes =========================== #

class BloomFilter:
    bit_array = bitarray(BLOOM_SIZE)
    bit_array.setall(0)

    def __init__(self, name):
        self.name = name

    def push(self, entry):
        for index in compute_hash_indexes(entry):
            print(f"[>>] Setting index: {index}")
            self.bit_array[index] = True  # Flip bit on


# Stored every 10 minutes
class DailyBloomFilter(BloomFilter):
    def __init__(self, name):
        super().__init__(name)
        self.age = 0

    # Called once a day for expiry management
    def update_age(self):
        self.age += 1


# Uploaded Every 60 minutes
class QueryBloomFilter(BloomFilter):
    def __init__(self, name):
        super().__init__(name)


# Combine DBFs into a CBF
class ContactBloomFilter(BloomFilter):
    def __init__(self, name, dbfs):
        super().__init__(name)
        # OR each dbfs bitarray into the cbf bit array



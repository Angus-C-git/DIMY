# ============================= Imports ============================= #
import pyhash
import time
import threading
from datetime import datetime
from bitarray import bitarray

# =========================== Middlewares ============================ #

BLOOM_SIZE = 800000                 # 100KB
HASH_ROUNDS = 3                     # Compute 3 hashes for each entry
fnv_hash = pyhash.fnv1_32()
murmur_hash = pyhash.murmur3_32()
DBF_EXPIRY = 6                      # Only store dbfs newer than this

DEVICE_DBFS = []                    # The last index is the current DBF
# ============================ Functions ============================ #

# TODO: work out how best to interact with the current DBF
'''
Uses timing module to keep track of how long a DBF has been alive for.
Manages the global queue of DBFs popping entries which have a age equal
to 6 (representing a DBF older than 60 minutes).

Probably use this function to also generate new DBFs and store them to
the global array. 
'''


def maintain_dbfs(dbf_clock):
    # Generate a new DBF every day (dbf_clock)
    print(f"[>>] Generating new DBF")
    DEVICE_DBFS.append(DailyBloomFilter(f"DBF_{datetime.now().time()}"))

    print(f"[>>] Looking for stale DBFs @, {datetime.now()}")
    # If the device has stored more than DBF_EXPIRY dbfs remove the
    # oldest one
    if len(DEVICE_DBFS) > DBF_EXPIRY:
        print(f"[>>] Evicting DBF: {DEVICE_DBFS.pop(0).name}")

    time.sleep(dbf_clock)
    return maintain_dbfs(dbf_clock)


def compute_hash_indexes(entry):
    print("[>>] Computing 3 rounds of murmur hash")
    indexes = []
    prev_hash = entry
    for cr in range(0, HASH_ROUNDS):
        indexes.append(murmur_hash(prev_hash) % BLOOM_SIZE)
        prev_hash = str(murmur_hash(prev_hash))

    return indexes


# ========================== Runner Class =========================== #

class DBFManager(threading.Thread):
    def __init__(self, name, dbf_clock=600):
        threading.Thread.__init__(self)
        self.name = name
        self.dbf_clock = dbf_clock

    def run(self):
        print("[>>] Starting " + self.name)
        maintain_dbfs(self.dbf_clock)
        print("[>>] Exiting " + self.name)
        return


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
    def __init__(self, name):
        super().__init__(name)
        print(f"[>>] Creating CBF from current DBFs: {[x.name for x in DEVICE_DBFS]}")
        # OR each dbfs bitarray into the cbf bit array


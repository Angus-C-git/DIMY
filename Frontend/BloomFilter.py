# ============================= Imports ============================= #
import pyhash
import time
import threading
from datetime import datetime
from bitarray import bitarray
import requests

# =========================== Middlewares ============================ #

API_BASE = 'http://ec2-3-26-37-172.ap-southeast-2.compute.amazonaws.com:9000/comp4337'

BLOOM_SIZE = 800000  # 100KB
HASH_ROUNDS = 3  # Compute 3 hashes for each entry
fnv_hash = pyhash.fnv1_32()
murmur_hash = pyhash.murmur3_32()
DBF_EXPIRY = 6  # Only store dbfs newer than this

DEVICE_DBFS = []  # The last index is the current DBF
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
    time.sleep(dbf_clock)

    print('\n<', ':' * 30, '[TASK-7 :: SEGMENT-7 :: B]', ':' * 30, '>\n')

    # Generate a new DBF every day (dbf_clock)
    print(f"[>>] Generating new DBF")
    DEVICE_DBFS.append(DailyBloomFilter(f"DBF_{datetime.now().time()}"))
    device_dbf_state = [dbf.name for dbf in DEVICE_DBFS]
    print(f"[>>] Stored DBFS: {device_dbf_state}")

    print(f"[>>] Looking for stale DBFs @, {datetime.now()}")
    # If the device has stored more than DBF_EXPIRY dbfs remove the
    # oldest one
    if len(DEVICE_DBFS) > DBF_EXPIRY:
        print(f"[>>] Evicting DBF: {DEVICE_DBFS.pop(0).name}")

    return maintain_dbfs(dbf_clock)


def upload_qbf(upload_clock):
    time.sleep(upload_clock)
    print('\n<', ':' * 30, '[TASK-8 :: SEGMENT-8 :: A]', ':' * 30, '>\n')
    send_qbf(QueryBloomFilter("DAILY_QBF"))


# TODO: Need to seed these hashes instead of using different ones
def compute_hash_indexes(entry):
    print("[>>] Computing 3 rounds of murmur hash")
    return [murmur_hash(entry, seed=murmur_hash('seed1')) % BLOOM_SIZE,
            murmur_hash(entry, seed=murmur_hash('seed2')) % BLOOM_SIZE,
            murmur_hash(entry, seed=murmur_hash('seed3')) % BLOOM_SIZE]


# ========================== Runner Classes =========================== #

class DBFManager(threading.Thread):
    def __init__(self, name, dbf_clock=600):
        threading.Thread.__init__(self)
        self.name = name
        self.dbf_clock = dbf_clock

    def run(self):
        # print("[>>] Starting " + self.name)
        maintain_dbfs(self.dbf_clock)
        # print("[>>] Exiting " + self.name)
        return


class QBFManager(threading.Thread):
    def __init__(self, name, qbf_clock=600):
        threading.Thread.__init__(self)
        self.name = name
        self.qbf_clock = qbf_clock

    def run(self):
        # print("[>>] Starting " + self.name)
        upload_qbf(self.qbf_clock)
        # print("[>>] Exiting " + self.name)
        return


# ========================== Bloom Classes =========================== #

class BloomFilter:
    bit_array = bitarray(BLOOM_SIZE)

    def __init__(self, name):
        self.name = name
        self.bit_array.setall(0)

    def push(self, entry):
        print('\n<', ':' * 30, '[TASK-7 :: SEGMENT-7 :: A]', ':' * 30, '>\n')
        # TODO print DBF 'state'
        for index in compute_hash_indexes(entry):
            # print(f"[>>] Setting index: {index}")
            self.bit_array[index] = True  # Flip bit on

        print(f"[>>] Current DBF State Post Insert: {[i[0] for i in enumerate(self.bit_array.tolist()) if i[1]]} \n")


# Stored every 10 minutes
class DailyBloomFilter(BloomFilter):
    def __init__(self, name):
        super().__init__(name)
        self.age = 0


# Uploaded Every 60 minutes
class QueryBloomFilter(BloomFilter):
    def __init__(self, name):
        super().__init__(name)
        # TODO: combine DBFs

        # TODO: send_qbf


# Combine DBFs into a CBF
class ContactBloomFilter(BloomFilter):
    def __init__(self, name):
        decision = str(input("Do you wish to upload your close contacts? Y/n")).lower()
        if decision == 'n':
            return

        super().__init__(name)
        print(f"[>>] Creating CBF from current DBFs: {[x.name for x in DEVICE_DBFS]}")
        # OR each dbfs bitarray into the cbf bit array



'''
Handles sending CBFs || QBFs to the backend api.
'''


def send_cbf(cbf):
    try:
        CBF = {"CBF": cbf}
        res = requests.post(f'{API_BASE}/cbf/upload', json=CBF)
        print(f"[>>] API RES => {res.json()}")
    except Exception as err:
        print(f"[>>] Failed to upload CBF to API, ERROR: {err}")

    return


def send_qbf(qbf):
    try:
        QBF = {"QBF": qbf}
        res = requests.post(f'{API_BASE}/qbf/query', json=QBF)
        print(f"[>>] API RES => {res.json()}")
    except Exception as err:
        print(f"[>>] Failed to upload QBF to API, ERROR: {err}")

    return

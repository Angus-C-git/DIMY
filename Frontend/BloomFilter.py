# ============================= Imports ============================= #
import pyhash
import time
import threading
from datetime import datetime
from bitarray import bitarray
from copy import deepcopy
from bitarray.util import ba2base
import requests
import base64

# =========================== Middlewares ============================ #

API_BASE = 'http://ec2-3-26-37-172.ap-southeast-2.compute.amazonaws.com:9000/comp4337'

BLOOM_SIZE = 20  # 100KB TODO: RESTORE THIS
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

    print(f"[>>] Combine DBFs into QBF @{datetime.now()}")

    # Upload the QBF to the API
    send_qbf(QueryBloomFilter("DAILY_QBF").get_bit_array())


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

    def __init__(self, name):
        self.name = name
        self.bit_array = bitarray(BLOOM_SIZE)
        self.bit_array.setall(0)

    def push(self, entry):
        print('\n<', ':' * 30, '[TASK-7 :: SEGMENT-7 :: A]', ':' * 30, '>\n')

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
        global DEVICE_DBFS
        super().__init__(name)
        # Combine all available DBFs into a QBF
        for dbf_index in DEVICE_DBFS:
            # print(f"DBF NAME: {dbf_index.name}, BA: {dbf_index.bit_array}")
            # print(f" {self.bit_array} OR {dbf_index.bit_array}")
            self.bit_array |= dbf_index.bit_array
            # print(f"RESULT: {self.bit_array}")
        print(f"[>>] Created QBF from current DBFs: {[x.name for x in DEVICE_DBFS]}")

    def get_bit_array(self):
        return self.bit_array


# Combine DBFs into a CBF
class ContactBloomFilter(BloomFilter):
    def __init__(self, name):
        super().__init__(name)
        # Combine all available DBFs into a CBF
        for dbf in DEVICE_DBFS:
            self.bit_array |= dbf.bit_array

        self.decision = str(input("Do you wish to upload your close contacts Y/n? ")).lower()
        if self.decision == 'n':
            return

        print(f"[>>] Combine DBFs into CBF @{datetime.now()}")
        print(f"[>>] Created CBF from current DBFs: {[x.name for x in DEVICE_DBFS]}")
        # OR each dbfs bitarray into the cbf bit array


'''
Handles sending CBFs || QBFs to the backend api.
'''


def send_cbf(cbf):
    try:
        CBF = {"CBF": base64.b64encode(cbf).decode('ascii')}
        print("[>>] Uploading CBF ... ")
        res = requests.post(f'{API_BASE}/cbf/upload', json=CBF)

        print('\n<', ':' * 30, '[TASK-10 :: SEGMENT-10 :: A]', ':' * 30, '>\n')

        print(f"[>>] Result: {res.json()['result']}, {res.json()['message']}")
    except Exception as err:
        print(f"[>>] Failed to upload CBF to API, ERROR: {err}")

    return


def send_qbf(qbf):
    try:
        # QBF = {"QBF": ba2base(64, qbf)}
        QBF = {"QBF": base64.b64encode(qbf).decode('ascii')}
        # print(f"PRE_UPLOAD_QBF {QBF}, Bits: {qbf}")
        print("[>>] Uploading QBF ... ")
        res = requests.post(f'{API_BASE}/qbf/query', json=QBF)

        print('\n<', ':' * 30, '[TASK-9 :: SEGMENT-9 :: A:B]', ':' * 30, '>\n')

        print(f"[>>] Result: {res.json()['result']}, Message: {res.json()['message']}")
    except Exception as err:
        print(f"[>>] Failed to upload QBF to API, ERROR: {err}")

    return

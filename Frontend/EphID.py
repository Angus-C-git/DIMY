# ============================= Imports ============================= #
import secrets
import pyhash
import time
import threading
from sslcrypto import ecc
from sslib import shamir
from Network import BroadcastRunner, Dh
from BloomFilter import DEVICE_DBFS

murmur_hash = pyhash.murmur3_32()
REGEN_CLOCK = 60  # Generate new EPhID Every Minute
N_SHARES = 6
K_FRAGMENTS = 3
PRIME_MOD = 2 ** 521 - 1


# ========================== Runner Class =========================== #

class EphIDRunner(threading.Thread):

    def __init__(self, name, eph_id, eph_clock=60):
        threading.Thread.__init__(self)
        self.name = name
        self.eph_clock = eph_clock
        self.eph_id = eph_id

    def run(self):
        # print("[>>] Starting " + self.name)
        regenerate_eph_id(self.eph_id)
        # print("[>>] Exiting " + self.name)
        return


'''
    init: generate new 128 bit EphID represented by a public key
'''


class EphID:
    n_shares = []
    current_eph_id = None
    current_eph_id_hash = None

    def __init__(self, name):
        self.name = name
        curve = ecc.get_curve("secp128r1")
        private_key = curve.new_private_key(is_compressed=True)
        public_key = curve.private_to_public(private_key)

        self.current_eph_id = public_key
        self.current_eph_id_hash = murmur_hash(self.current_eph_id)

        self.gen_chunks()

    def gen_chunks(self):
        shares_dict = shamir.to_hex(
            shamir.split_secret(self.current_eph_id, K_FRAGMENTS, N_SHARES, prime_mod=PRIME_MOD))
        self.n_shares = shares_dict.get("shares")
        return


# ============================ Functions ============================ #

# TODO: THIS IS SO SLOW THAT IT PUTS OFF WHOLE SYS CLOCK
def regenerate_eph_id(eph_id):
    while True:
        time.sleep(REGEN_CLOCK)

        print('\n<', ':' * 30, '[TASK-1 :: SEGMENT-1 :: A]', ':' * 30, '>\n')
        eph_id = EphID("NEW_EPH_ID")
        print(f"[>>] Generated New EphID: {eph_id.current_eph_id.hex()}")
        print(f"[>>] EphID Hash {hex(eph_id.current_eph_id_hash)}")

        BROADCAST_SVR = BroadcastRunner("BROADCAST_THREAD", eph_id.n_shares, eph_id.current_eph_id_hash, 0)
        BROADCAST_SVR.start()


def integrity_check(advert_hash, recovered_ehp_id):
    # Determine if a given eph_id matches the one in the adverts
    recovered_hash = murmur_hash(recovered_ehp_id)
    print(f"[>>] Hash Of Recovered EphID: {hex(recovered_hash)}")
    print(f"[>>] Hash Of Advertised EphID: {hex(int(advert_hash))}")

    if int(advert_hash) == int(recovered_hash):
        print("[>>] Integrity Check Passed")
        # TODO :::::::: Generate EncID from here @lucy ::::::::
        dh = Dh()
        encID = dh.get_shared_key()

        current_dbf = DEVICE_DBFS[-1]
        print(f"[>>] Encoding EncID: {str(encID)}  into: {current_dbf.name}, with: 3 murmur "
              f"hashes")
        current_dbf.push(str(encID))
    else:
        print("[>>] Integrity Check Failed, discard match")
        return


def reconstruct_shares(shares, advert_hash):
    section_head = 30
    print('\n<', ':' * section_head, '[TASK-4 ::SEGMENT-4 :: A:B]', ':' * section_head, '>\n')

    shamir_dict = {
        'required_shares': 3,
        'prime_mod': PRIME_MOD,
        'shares': shares
    }

    recovered_secret = shamir.recover_secret(shamir.from_hex(shamir_dict))
    print(f"[>>] Recovered EphID: {recovered_secret.hex()}")
    integrity_check(advert_hash, recovered_secret)

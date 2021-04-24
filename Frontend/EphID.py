# ============================= Imports ============================= #
import secrets
import pyhash
import time
import threading
from sslcrypto import ecc
from sslib import shamir
from Network import BroadcastRunner

murmur_hash = pyhash.murmur3_32()


# ========================== Runner Class =========================== #

class EphIDRunner(threading.Thread):

    def __init__(self, name, eph_id, eph_clock=60):
        threading.Thread.__init__(self)
        self.name = name
        self.eph_clock = eph_clock
        self.eph_id = eph_id

    def run(self):
        print("[>>] Starting " + self.name)
        regenerate_eph_id(self.eph_id)
        print("[>>] Exiting " + self.name)
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
        # TODO: unfortunate code_reuse --> Could probably just call the constructor instead of regen
        curve = ecc.get_curve("secp128r1")
        private_key = curve.new_private_key(is_compressed=True)
        public_key = curve.private_to_public(private_key)

        self.current_eph_id = public_key
        self.current_eph_id_hash = murmur_hash(self.current_eph_id)

        # print(f"[>>] EphID: {self.current_eph_id}")
        self.gen_chunks()

    def gen_chunks(self):
        k = 3
        n = 6
        # print("[>>] Generating shares")
        shares_dict = shamir.to_hex(shamir.split_secret(self.current_eph_id, k, n))
        # shares_dict = shamir.to_base64(shamir.split_secret(self.current_eph_id, k, n))
        # print(f"[>>] Shares: {shares_dict}")
        self.n_shares = shares_dict.get("shares")
        # # TODO: Start broadcasting
        # broadcaster = BroadcastRunner("BROADCAST_RUNNER", self.n_shares, 0)
        # broadcaster.start()
        # broadcaster.join()

        return

    # def regenerate_eph_id(self):
    #     while True:
    #         time.sleep(self.eph_clock)
    #         curve = ecc.get_curve("secp128r1")
    #         private_key = curve.new_private_key()
    #         public_key = curve.private_to_public(private_key)
    #
    #         self.current_eph_id = public_key
    #         print(f"[>>] EphID: {self.current_eph_id}")
    #         self.gen_chunks()
    #         # time.sleep(self.eph_clock)


# ============================ Functions ============================ #

def regenerate_eph_id(eph_id):
    while True:
        time.sleep(10)

        eph_id = EphID("NEW_EPH_ID")
        print(f"[>>] Generated New EphID: {eph_id.current_eph_id.hex()}")


def integrity_check(share):
    # Determine if a given shares hash is valid

    return share


def reconstruct_shares(shares):
    print(f"[>>] Reconstructing shares {shares}")
    shamir_dict = {
        'required_shares': 3,
        'prime_mod': '010000000000000000000000000000000000000000000000000000000000000000000000000000001b',
        'shares': shares
    }

    recovered_secret = shamir.recover_secret(shamir.from_hex(shamir_dict))
    print(f"[>>] Recovered Secret {recovered_secret}")
    return shares

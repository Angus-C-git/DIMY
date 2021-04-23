# ============================= Imports ============================= #
import secrets
import pyhash
import time
import threading
from sslcrypto import ecc
from sslib import shamir

# ========================== Runner Class =========================== #


'''
    init: generate new 128 bit EphID represented by a public key
'''


class EphIDRunner(threading.Thread):
    n_shares = []
    private_key = None
    current_eph_id = None

    def __init__(self, name, eph_clock=60):
        threading.Thread.__init__(self)
        self.name = name
        self.eph_clock = eph_clock

    def run(self):
        print("[>>] Starting " + self.name)
        self.regenerate_eph_id()
        print("[>>] Exiting " + self.name)
        return

    def gen_chunks(self):
        k = 3
        n = 6
        print("[>>] Generating shares")
        shares_dict = shamir.to_hex(shamir.split_secret(self.current_eph_id, k, n))
        # shares_dict = shamir.to_base64(shamir.split_secret(self.current_eph_id, k, n))
        print(f"[>>] Shares: {shares_dict}")

        self.n_shares = shares_dict.get("shares")
        return

    def regenerate_eph_id(self):
        while True:
            curve = ecc.get_curve("secp128r1")
            private_key = curve.new_private_key()
            public_key = curve.private_to_public(private_key)

            self.current_eph_id = public_key
            print(f"[>>] EphID: {self.current_eph_id}")
            self.gen_chunks()
            time.sleep(self.eph_clock)

    def broadcast_shares(self):
        return


def integrity_check(share):
    # Determine if a given shares hash is valid

    return share


def reconstruct_shares(shares):
    print(f"[>>] Reconstructing shares {shares}")
    return shares


# ========================== RANDOM NOTES ============================== #

'''
EphID is the public key from the SECP128r1 ECDH library
'''

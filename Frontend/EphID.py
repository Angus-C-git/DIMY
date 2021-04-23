# ============================= Imports ============================= #
import secrets
import pyhash
from ecdsa import ECDH, NIST256p
from ecdsa.curves import *
from ecdsa import *
# ============================= Classes ============================= #


class EphID:
    n_shares = []

    def __init__(self):
        self.eph_id = secrets.token_bytes(16)  # EphID is 16 bytes = 128 bits

    def gen_chunks(self):
        return

    def regenerate_eph_id(self):
        # self.eph_id = secrets.token_bytes(16)
        ecdh = ECDH(curve=NIST256p)
        self.eph_id = ecdh.get_public_key()

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

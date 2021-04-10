import secrets


class EphID:
    n_shares = []

    def __init__(self):
        self.eph_id = secrets.token_bytes(16)

    def gen_chunks(self):
        return

    def regenerate_eph_id(self):
        self.eph_id = secrets.token_bytes(16)

    def broadcast_shares(self):
        return



def reconstruct_shares(shares):
    print(f"[>>] Reconstructing shares {shares}")
    return shares
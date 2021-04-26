# ============================= Imports ============================= #

import socket
import threading
import requests
import time
import mmh3
import sslcrypto
import EphID
from tinyec import registry
import secrets
from Resolve import get_host_ip

# ============================ Middlewares =========================== #

PORT = 2048
PORT2 = 2049
BROADCAST_IP = '192.168.8.5'  # Broadcast address (send to all clients)
IP_LISTENER = get_host_ip()

RECONSTRUCT_THRESHOLD = 3
BROADCAST_RATE = 10  # Broadcast one share/10 sec


# =========================== Diffie Hellman ========================= #

class Dh:
    def __init__(self):
        self.priv_key, self.pub_key = self.generate_dh()
        self.shared_key = None
        self.share_dh()
        
    def generate_dh(self):
        # Save the curve, a particular curve used in ECDH
        curve = registry.get_curve('secp192r1')

        priv_key = secrets.randbelow(curve.field.n)
        pub_key = priv_key * curve.g

        return priv_key, self.compress(pub_key)

    def share_dh(self):
        try:
            tsend = threading.Thread(target=self.send_dh, args=())
            treceive = threading.Thread(target=self.receive_dh, args=())

            treceive.start()
            tsend.start()
            tsend.join()
            treceive.join()

        except Exception as e:
            print(f"[>>] Unable to start thread ERROR: {e}")

    def send_dh(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock.sendto(self.pub_key.encode('ascii'), (BROADCAST_IP, PORT2))

    def receive_dh(self):
        rec_pub_key = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener = (IP_LISTENER, PORT2)
        sock.bind(listener)

        # print(f"[>>] DH Listener is live IP: <{IP_LISTENER}> PORT: <{PORT2}> Hostname: <{socket.gethostname()}>")

        while rec_pub_key is None:
            try:
                packet, sender = sock.recvfrom(4096)  # Receive share in 4069 bit buffer??
                rec_pub_key = packet.decode('ascii')
                # print(f"[>>] Received public key => {rec_pub_key}")
                # return rec_pub_key
            except Exception as err:
                print(f"[>>] Receiver died, ERROR: {err}")

        # print(int(rec_pub_key, 16) * self.priv_key)
        self.shared_key = int(rec_pub_key, 16) * self.priv_key
        return

    def compress(self, key):
        return hex(key.x) + hex(key.y % 2)[2:]

    def get_shared_key(self):
        return self.shared_key

    def delete_shared_key(self):
        self.shared_key = None

# ======================== Networking Runners ======================== #


class ReceiverRunner(threading.Thread):
    def __init__(self, name, test_mode):
        threading.Thread.__init__(self)
        self.name = name
        self.test_mode = test_mode

    def run(self):
        # print("[>>] Starting " + self.name)
        receive_advertisements(self.test_mode)
        # print("[>>] Exiting " + self.name)
        return


class BroadcastRunner(threading.Thread):
    def __init__(self, name, shares, advert_hash, test_mode):
        threading.Thread.__init__(self)
        self.name = name
        self.test_mode = test_mode
        self.shares = shares
        self.advert_hash = advert_hash

    def run(self):
        # print("[>>] Starting " + self.name)
        broadcast_share(self.shares, self.advert_hash, self.test_mode, 0)
        # print("[>>] Exiting " + self.name)
        return


# ============================ Functions ============================ #


'''
Handles broadcasting of EphID shares.
Will be run by a thread.
'''


def broadcast_share(shares, advert_hash, test_mode, cnt):
    # If we have broadcast all the shares exit
    if not shares:
        return

    try:
        # TODO: work out how to broadcast along the whole IP address block
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

        print(f"[>>] Sending share => {shares[0]}")
        advertisement = f'{advert_hash}|{shares[0]}'
        # sock.sendto(shares[0].encode('ascii'), (IP_LISTENER, PORT))  # TODO:::: THIS NEEDS TO BE BROADCAST
        sock.sendto(advertisement.encode('ascii'), (BROADCAST_IP, PORT))

        # remove the share we just broadcast
        shares.pop(0)
        if test_mode:
            cnt += 1
            if cnt >= 3:
                return

        # Broadcast one share/10s
        time.sleep(BROADCAST_RATE)
        return broadcast_share(shares, advert_hash, test_mode, cnt)
    except Exception as e:
        print(f"[>>] Broadcaster died, ERROR: {e} attempting restart")
        time.sleep(10)
        return broadcast_share(shares, test_mode, advert_hash, cnt)


'''
Handel receiving shares of EphIDs.
Will be run by a runner thread indefinitely.

TODO: 

    - If multiple senders are involved will need to track multiple share groups
        one per sender
    - The metric is at least n shares (n = 3) should the share buffer be whipped then 
        after receiving n shares ? 
'''


def receive_advertisements(test_mode):
    shares = []  # Store buffer of received shares
    # The prime_mod is a fixed value for the shamir library necessary for reconstruction

    #    - Initialise Listener -    #

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener = (IP_LISTENER, PORT)
    sock.bind(listener)

    print(f"[>>] Listener is live IP: <{IP_LISTENER}> PORT: <{PORT}> Hostname: <{socket.gethostname()}>")

    while True:
        try:
            packet, sender = sock.recvfrom(4096)  # Receive share in 4069 bit buffer??
            advertisement = packet.decode('ascii')

            # Need to split dynamically instead
            # print(f"[>>] ADVERTISEMENT: {advertisement.split('|')}")
            advertisement = advertisement.split('|')

            advert_hash = advertisement[0]
            share = advertisement[1]
            print(f"[>>] Received Share [{len(shares) + 1}/6] <= {share}")
            shares.append(share)
            if len(shares) == 3 or len(shares) == 6:
                EphID.reconstruct_shares(shares, advert_hash)
                if len(shares) == 6:
                    shares = []  # reset shares buffer

                if test_mode:
                    return
        except Exception as err:
            print(f"[>>] Receiver died due to lib, ERROR: {err}, attempting restart ...")
            sock.detach()
            receive_advertisements(test_mode)



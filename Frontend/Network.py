# ============================= Imports ============================= #

import socket
import threading
import requests
import time
import mmh3
import sslcrypto
import EphID
from Resolve import get_host_ip

# ============================ Middlewares =========================== #

PORT = 2049
BROADCAST_IP = '192.168.4.255'  # Broadcast address (send to all clients)
IP_LISTENER = get_host_ip()
API_BASE = 'http://ec2-3-26-37-172.ap-southeast-2.compute.amazonaws.com:9000/comp4337'

RECONSTRUCT_THRESHOLD = 3
BROADCAST_RATE = 10  # Broadcast one share/10 sec


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
        print("[>>] Exiting " + self.name)
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

        # tmp_share = "some_share_n"
        print(f"[>>] Sending share => {shares[0]}")
        # TODO: TMP send hash
        advertisement = f'{advert_hash}|{shares[0]}'
        # sock.sendto(shares[0].encode('ascii'), (IP_LISTENER, PORT))  # TODO:::: THIS NEEDS TO BE BROADCAST
        sock.sendto(advertisement.encode('ascii'), (IP_LISTENER, PORT))
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
            # print(f'[>>] ADVERTISEMENT: {advertisement}')
            advert_hash = advertisement[:10]
            share = advertisement[11:]
            print(f"[>>] Received Share [{len(shares) + 1}/6] <= {share}")
            shares.append(share)
            # TODO:::: This is poor logic
            if len(shares) == 3 or len(shares) == 6:
                EphID.reconstruct_shares(shares, advert_hash)
                if len(shares) == 6:
                    shares = []  # reset shares buffer

                if test_mode:
                    return
        except Exception as err:
            print(f"[>>] Receiver died, ERROR: {err}, attempting restart ...")
            receive_advertisements(test_mode)


'''
Handles sending CBFs || QBFs to the backend api.
'''


def send_cbf(cbf):
    try:
        CBF = {"CBF": cbf}
        res = requests.post(f'{API_BASE}/cbf/upload', json=CBF)
        print(f"[>>] API RES => {res.json()}")
    except:
        print("[>>] Failed to upload CBF to API")

    return


def send_qbf(qbf):
    try:
        QBF = {"QBF": qbf}
        res = requests.post(f'{API_BASE}/qbf/query', json=QBF)
        print(f"[>>] API RES => {res.json()}")
    except:
        print("[>>] Failed to upload QBF to API")

    return

# ========================= Imports ========================= #

import socket
import threading
import requests
import time
import EphID
from Resolve import get_host_ip

# ========================= Middlewares ========================= #

# TODO: Replace hardcoded values
PORT = 2048
IP_RANGE = '192.168.4.1/24'
IP_LISTENER = get_host_ip()  # This machines IP


# ========================= Networking Runners ========================= #

class ReceiverRunner(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("[>>] Starting " + self.name)
        receive_shares()
        print("[>>] Exiting " + self.name)


class BroadcastRunner(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("[>>] Starting " + self.name)
        broadcast_share("tmp_share")  # TODO: get from function
        print("[>>] Exiting " + self.name)


# ========================= Functions ========================= #

'''
Handles broadcasting of EphID shares.
Will be run by a thread
'''


def broadcast_share(share):
    try:
        # TODO: work out how to broadcast along the whole IP address block
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

        # tmp_share = "some_share_n"
        print(f"[>>] Sending share {share}")
        sock.sendto(share.encode('utf=8'), (IP_LISTENER, PORT))
        # Broadcast one share/10s
        time.sleep(10)
        return broadcast_share(share)
    except:
        print("[>>] Broadcaster died, attempting restart")
        return broadcast_share(share)


'''
Handel receiving shares of EphIDs.
Will be run by a runner thread indefinitely.

TODO: 

    - If multiple senders are involved will need to track multiple share groups
        one per sender
    - The metric is at least n shares (n = 3) should the share buffer be whipped then 
        after receiving n shares ? 
'''


def receive_shares():
    shares = []  # Store buffer of received shares

    #    - Initialise Listener -    #

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener = (IP_LISTENER, PORT)
    sock.bind(listener)

    print(f"[>>] Listener is live IP: <{IP_LISTENER}> PORT: <{PORT}>")
    print(f"[>>] Hostname: {socket.gethostname()}")

    while True:
        try:
            packet, sender = sock.recvfrom(4096)  # Receive share in 4069 bit buffer??
            share = packet.decode('utf-8')  # TODO: decode from b64 || hex
            print(f"[>>] Received Share => {share}")
            shares.append(share)
            if len(shares) >= 3:
                EphID.reconstruct_shares(shares)
                shares = []  # reset shares buffer
        except:
            print("[>>] Receiver died, attempting restart ...")
            receive_shares()


'''
Handles sending CBFs || QBFs to the backend api.
'''


def send_cbf(cbf):
    API_ENDPOINT = 'http://ec2-3-25-246-159.ap-southeast-2.compute.amazonaws.com:9000/comp4337/cbf/upload'
    try:
        CBF = {"CBF": cbf}
        res = requests.post(API_ENDPOINT, json=CBF)
        print(f"[>>] API RES => {res.json()}")
    except:
        print("[>>] Failed to upload CBF to API")

    return


def send_qbf(qbf):
    API_ENDPOINT = 'http://ec2-3-25-246-159.ap-southeast-2.compute.amazonaws.com:9000/comp4337/qbf/query'
    try:
        QBF = {"QBF": qbf}
        res = requests.post(API_ENDPOINT, json=QBF)
        print(f"[>>] API RES => {res.json()}")
    except:
        print("[>>] Failed to upload QBF to API")

    return

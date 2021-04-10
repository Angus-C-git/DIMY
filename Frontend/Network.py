# ========================= Imports ========================= #

import socket
import threading
import requests
import time
import EphID

# ========================= Middlewares ========================= #

PORT = 2048
IP_RANGE = '192.168.4.1/24'
IP_LISTENER = '100.95.249.235'  # This machines IP


# ========================= Network Runner ========================= #

class NetworkRunner(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("Starting " + self.name)
        receive_shares()
        print("Exiting " + self.name)


# ========================= Functions ========================= #

'''
Handles broadcasting of EphID shares.
Will be run by a thread
'''


def broadcast_share(share):
    # TODO: work out how to broadcast along the whole IP address block

    # Broadcast one share/10s
    time.sleep(10)
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
    shares = []  # Store buffer of recived shares

    ####### - Initialise Listener - #######

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener = (IP_LISTENER, PORT)
    sock.bind(listener)

    print(f"[>>] Listener is live IP <{IP_LISTENER}> PORT <{PORT}>")

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


def send_bloom_filter():
    return

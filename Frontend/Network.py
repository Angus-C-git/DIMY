# ========================= Imports ========================= #

import socket
import requests
import time
import EphID

# ========================= Middlewares ========================= #

PORT = 2048
IP_RANGE = '192.168.4.1/24'
IP_LISTNER = '192.168.4.25' # This machines IP

# ========================= Functions ========================= #

'''
Handels broadcasting of EphID shares.
Will be run by a thread
'''
def broadcast_share(share):

    # Brodcast one share/10s
    time.sleep(10)
    return broadcast_share(share)


'''
Handel reciving shares of EphIDs.
Will be run by a runner thread indefinetly.

TODO: 

    - If multiple senders are involved will need to track multiple share groups
        one per sender
    - The metric is at least n shares (n = 3) should the share buffer be whiped then 
        after reciving n shares ? 
'''
def recive_shares():
    shares = [] # Store buffer of recived shares

    ####### - Initialise Listener - #######

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(IP_LISTNER, PORT)

    print(f"[>>] Listner is live IP <{IP_LISTNER}> PORT <{PORT}>")

    while True:
        try:
            packet, sender = sock.recvfrom(4096) # Recive share in 4069 bit buffer??
            share = packet.decode('utf-8')  # TODO: decode from b64 || hex
            print(f"[>>] Recived Share => {share}")
            shares.append(share)
            if len(shares) >= 3:
                EphID.reconstruct_shares(shares)
                shares = [] # reset shares buffer
        except:
            print("[>> Reciver died, attempting restart ...")
            recive_shares()


'''
Handels sending CBFs || QBFs to the backend api.
'''
def send_bloom_filter():
    return

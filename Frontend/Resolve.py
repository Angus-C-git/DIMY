import socket
"""
Contains various helper functions for
the network stack.
"""


'''
Resolve the devices broadcast IP address for Networking stack
functions.
'''


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
    s.close()
    return IP

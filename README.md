# DIMY

Digital Contact Tracing Protocol using UDP/TCP.


## Overview

![DIMY Protocol Overview](./images/DIMYOverviewDiagram.svg)


## Implementation Details

+ For ECHD generation the library `sslcrypto` is used
    + The extra bit flag from the generation of the 16 byte public key is 
      discarded before transmission
+ All hashing is done using the `murmurhash3` hash algorithm



## Usage

1. Run `pip3 install -r requirments.txt`
2. Since our broadcast address is not working you will need to edit the BROADCAST_IP feild in Network.py on both clients to be the others IP
3. Run `python3 Frontend/Dimy.py`


## Known Issues

1. For some reason the EphID takes a very longtime to generate around 60% of the time which slows down the whole system
2. Broadcast address does not work on tested network

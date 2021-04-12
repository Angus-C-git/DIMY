# DIMY

Digital Contact Tracing Protocol using UDP/TCP.


## Overview

![DIMY Protocol Overview](./images/DIMYOverviewDiagram.svg)


## Implementation Details

+ For ECHD generation the library `sslcrypto` is used
    + The extra bit flag from the generation of the 16 byte public key is 
      discarded before transmission
+ All hashing is done using the `murmurhash3` hash algorithm
# Stratum Mining Protocol for Sia

```
Original Release Date: 2016-07-21
```

## Motivation

Previous attempts at adapting the Stratum protocol so that it could be used for mining cryptocurrencies which, like Sia, show significant differences from Bitcoin took an approach that could be described as “getwork over Stratum”, or “getwork over TCP”. What this means is that they sent the same header data that would be sent by the old getwork-style protocol, only packed inside the fields of the original Stratum protocol, which were meant to carry different data. Such an approach retains of course the advantage of removing the overhead of HTTP, but has also clear downsides when compared to the original Stratum protocol:

*   It is not scalable. The original Stratum design enables pools and large mining operations to easily handle large numbers of miners, as there is no need for servers to remember about each and every work unit they hand out. Less load on servers also means that servers can be faster and more responsive.
*   It is not future-proof, as it does not extend the nonce space. Even if Sia has a larger header nonce than Bitcoin, providing additional variable-length nonce space is the only way for a mining protocol to be truly future-proof. One immediate benefit of this is that mining proxies can be used to optimize the efficiency of mining networks.

For the above reasons, SiaMining.com decided to develop a true Stratum protocol for Sia.

One of the main objectives was to stay as close as possible to the original Stratum protocol. This makes the implementation easier and allows for better software compatibility.

## Specification

Unless otherwise specified, everything works in the same way as described by the [Stratum mining protocol specification for Bitcoin](https://slushpool.com/help/#!/manual/stratum-protocol). In particular, the names and parameter counts remain the same for all methods and notifications.

### Encoding

All hexadecimally-encoded data is serialized as specified by the Sia protocol. No endianness conversion is performed.

### Notifications

Differences:

*   The 6th parameter (`version`) is unused, and should be empty.
*   The 7th parameter (`nbits`) is not required for mining, but is provided to inform the miner of the current network difficulty. It must be the 32-bit compact representation of the current network target.
*   The 8th parameter (`ntime`) must be 16 hex characters long (64 bits).

Example:

```
{
    "params": [
        "bf",
        "000000000000052714f51ebea73d6310db96d54a8399c5802e42508ea2486717",
        "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000020000000000000004e6f6e536961000000000000000000000000000000000000",
        "0000000000000000",
        [ "356464cda3f7a83a350aeb3ae5101ff56799cd68ad48b475426141540876bd31", "9cb176ec5b06898ef40f0e73242e0b0ff9d34ece67a241d529f2c18c67c73803" ],
        "",
        "1a08645a",
        "58258e5700000000",
        false
    ],
    "id": null,
    "method": "mining.notify"
}
```

### Building the Arbitrary Transaction

Due to the differences between the Bitcoin block format and the Sia block format, the coinbase transaction is replaced here by a so-called arbitrary transaction. This transaction is built in the same way the coinbase transaction is: by concatenating `coinb1`, `extranonce1`, `extranonce2`, and `coinb2`.

What is different is how this transaction must be hashed: you have to prepend a null byte to the transaction, and then apply the same blake2b hashing function used by Sia.

You can consider the following Python snippet as a reference:

```
import binascii
from pyblake2 import blake2b

arbtx_hash_bin = blake2b('\x00' + binascii.unhexlify(arbtx), digest_size=32).digest()
```

### Computing the Merkle Root

The arbitrary transaction hash is the rightmost leaf of the Merkle tree rather than the leftmost.

For each of the `merkle_branch` hashes, prepend a single byte with a value of 1, and append the hash resulting from the previous iteration (or the hash of the arbitrary transaction for the first iteration). Apply blake2b to this 65-byte buffer.

The following Python snippet illustrates the process:

```
def build_merkle_root(merkle_branch, arbtx_hash_bin):
    merkle_root = arbtx_hash_bin
    for h in merkle_branch:
        merkle_root = blake2b('\x01' + binascii.unhexlify(h) + merkle_root, digest_size=32).digest()
    return merkle_root
```

### Building the Header

The 80-byte header is built by concatenating `prevhash` (32 bytes), a nonce (8 bytes), `ntime` (8 bytes), and the Merkle root (32 bytes).

### Submission

The only difference is that the 4th and 5th parameters (`ntime` and `nonce`) are 64-bit values, and must be 16 characters long.

Example:

```
{
    "params": [
        "slush.miner1",
        "bf",
        "00000001",
        "58258e5700000000",
        "b2957c0000000000"
    ],
    "id": 4,
    "method": "mining.submit"
}
```

### Difficulty

No changes here: we retain the same definition of difficulty used by Bitcoin and by the original Stratum protocol. Note that Sia uses a different (and more intuitive) definition of difficulty, and the two differ by a factor of about 4,295,032,833, which is slightly over 2<sup>32</sup>.

For Stratum, difficulty 1 corresponds to the target

```
0x00000000ffff0000000000000000000000000000000000000000000000000000,
```

while for Sia the difficulty-1 target is

```
0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff.
```

Please note that Stratum difficulties do not have to be integer numbers. For instance, it is common for pools to use targets like

```
0x00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff,
```

which corresponds to a Stratum difficulty of about 0.99998474121094105.

## Compatible Software

* [Marlin](https://siamining.com/marlin)
* [KlausT's ccminer](https://github.com/KlausT/ccminer)
* [sgminer](https://github.com/SiaMining/sgminer)
* [Stratum mining proxy](https://github.com/SiaMining/stratum-mining-proxy/)

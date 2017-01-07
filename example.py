#!/usr/bin/env python

from binascii import hexlify, unhexlify
from pyblake2 import blake2b

# Block 86011
# Hash 000000000000007384ca7ba61a988d14f9a9d731a981c186e8904f1e1d82e6f5
prevhash = '0000000000000079039da6f4d7790d54d774812f92e459387846524f4024afe3'
coinb1 = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000020000000000000004e6f6e536961000000000000000000006aba4dfb5df01095'
coinb2 = '0000000000000000'
merkle_branch = [
    '25cc1c464ed8f0a13da6c14098c2cd47526dcd64d3594a2ace794b9bc0ab704d',
    '2c162ebd012c0044cd34808a0dc9e5790f428cba73ce7b848a6f63ddd845c80e',
    '20283c26aa6cf99c126fe74021f2c5fb39baffd81814d725c57c883e16676c5d',
]
ntime = '2ed1705800000000'
extranonce1 = '99cfbade'
extranonce2 = 'ef7488b3'
nonce = '40371d049700e893'

def blake2b32(x):
    return blake2b(x, digest_size=32).digest()

def hash_arbtx(arbtx):
    return blake2b32(b'\x00' + unhexlify(arbtx))

def build_merkle_root(merkle_branch, arbtx_hash_bin):
    merkle_root = arbtx_hash_bin
    for h in merkle_branch:
        merkle_root = blake2b32(b'\x01' + unhexlify(h) + merkle_root)
    return merkle_root

arbtx = coinb1 + extranonce1 + extranonce2 + coinb2
arbtx_hash_bin = hash_arbtx(arbtx)
merkle_root_bin = build_merkle_root(merkle_branch, arbtx_hash_bin)
merkle_root = hexlify(merkle_root_bin).decode('ascii')
header = prevhash + nonce + ntime + merkle_root
header_bin = unhexlify(header)
header_hash = hexlify(blake2b32(header_bin)).decode('ascii')

print('Merkle Root:\n\t%s' % merkle_root)
print('Block Hash:\n\t%s' % header_hash)

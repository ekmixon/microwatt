#!/usr/bin/python3

b = bytearray()
for i in range(0x100):
    b = b + i.to_bytes(4, 'little')
with open('icache_test.bin', 'w+b') as f:
    f.write(b)


import struct
def load(d):
    n=struct.unpack_from('<I',d,0x10)[0]
    ents=[struct.unpack_from('<II',d,0x1c+8*i) for i in range(n)]  # (hash, off)
    out=[]
    for h,o in ents:
        L=struct.unpack_from('<I',d,o)[0];out.append((h,bytes(d[o+4:o+4+L])))
    return out
def build(orig,strings):
    d=bytearray(orig[:0x1c+8*len(strings)])
    pos=len(d);blob=bytearray()
    for i,(h,s) in enumerate(strings):
        struct.pack_into('<II',d,0x1c+8*i,h,pos+len(blob))
        blob+=struct.pack('<I',len(s))+s
    return bytes(d+blob)

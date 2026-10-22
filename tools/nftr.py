import struct
class NFTR:
    def __init__(s,data):
        s.d=bytearray(data);d=s.d;o=0x10
        while o<len(d):
            tag=bytes(d[o:o+4]);sz=struct.unpack_from('<I',d,o+4)[0]
            if tag==b'PLGC':
                s.cglp=o;s.w,s.h,s.bpg,s.bl,s.mw,s.bpp,_=struct.unpack_from('<BBHBBBB',d,o+8);s.ng=(sz-16)//s.bpg
            if tag==b'HDWC':s.cwdh=o
            if tag==b'PAMC':
                lo,hi,t=struct.unpack_from('<HHI',d,o+8)
                s.maps=getattr(s,'maps',[])+[(lo,hi,t,o+20)]
            o+=sz
        s.cmap={}
        for lo,hi,t,p in s.maps:
            if t==0:
                first=struct.unpack_from('<H',d,p)[0]
                for c in range(lo,hi+1):s.cmap[c]=first+c-lo
            elif t==1:
                for c in range(lo,hi+1):
                    g=struct.unpack_from('<H',d,p+2*(c-lo))[0]
                    if g!=0xffff:s.cmap[c]=g
            else:
                n=struct.unpack_from('<H',d,p)[0]
                for k in range(n):
                    c,g=struct.unpack_from('<HH',d,p+2+4*k);s.cmap[c]=g
        fi=struct.unpack_from('<H',d,s.cwdh+8)[0]
        s.wfirst=fi
    def glyph(s,i):
        o=s.cglp+16+i*s.bpg;b=s.d[o:o+s.bpg];px=[]
        for y in range(s.h):
            row=[]
            for x in range(s.w):
                k=(y*s.w+x)*s.bpp;row.append((b[k//8]>>(8-s.bpp-k%8))&((1<<s.bpp)-1))
            px.append(row)
        return px
    def setglyph(s,i,px):
        o=s.cglp+16+i*s.bpg;b=bytearray(s.bpg)
        for y in range(s.h):
            for x in range(s.w):
                v=px[y][x];k=(y*s.w+x)*s.bpp;b[k//8]|=v<<(8-s.bpp-k%8)
        s.d[o:o+s.bpg]=b
    def width(s,i):
        o=s.cwdh+16+(i-s.wfirst)*3;return tuple(s.d[o:o+3])
    def setwidth(s,i,t):
        o=s.cwdh+16+(i-s.wfirst)*3;s.d[o:o+3]=bytes(t)

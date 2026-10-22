"""모든 그래픽 렌더링 (검사용). nbfc/nbfp/nbfs 및 NCGR/NCLR"""
import ndspy.rom,struct,sys,os
from PIL import Image
r=ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]);out=sys.argv[2];os.makedirs(out,exist_ok=True)
names={(r.filenames.filenameOf(i) or ''):i for i in range(len(r.files))}
def pal(b):return [((c&31)*8,(c>>5&31)*8,(c>>10&31)*8) for c in struct.unpack('<%dH'%(len(b)//2),b)]
def tiles(b,bpp):
    sz=32 if bpp==4 else 64;T=[]
    for k in range(len(b)//sz):
        t=b[k*sz:(k+1)*sz]
        T.append([ (t[i//2]>>(4*(i&1)))&15 for i in range(64)] if bpp==4 else list(t))
    return T
def draw(T,P,mp,wt,bpp):
    ht=(len(mp)+wt-1)//wt;im=Image.new('RGB',(wt*8,ht*8))
    px=im.load()
    for n,e in enumerate(mp):
        ti=e&0x3ff;hf=e>>10&1;vf=e>>11&1;pb=(e>>12)*16 if bpp==4 else 0
        if ti>=len(T):continue
        t=T[ti]
        for y in range(8):
            for x in range(8):
                v=t[(7-y if vf else y)*8+(7-x if hf else x)]
                c=P[(pb+v)%len(P)] if v else (0,0,0)
                px[(n%wt)*8+x,(n//wt)*8+y]=c
    return im
cnt=0
for n,i in names.items():
    if n.endswith('.nbfc'):
        base=n[:-5];c=r.files[i]
        p=names.get(base+'.nbfp');s=names.get(base+'.nbfs')
        P=pal(r.files[p]) if p is not None else [(v*16,v*16,v*16) for v in range(16)]
        bpp=8 if len(P)>16 else 4
        T=tiles(c,bpp)
        if s is not None:
            mp=struct.unpack('<%dH'%(len(r.files[s])//2),r.files[s]);
            if bpp==8:mp=[e&0x3ff|(e&0xc00) for e in mp]
        else:mp=list(range(len(T)))
        wt=32 if len(mp)%32==0 and len(mp)>=256 else (16 if len(mp)>=64 else max(1,len(mp)))
        im=draw(T,P,mp,wt,bpp)
        # 맵 없이 타일 순서 보기도 함께
        im.save(os.path.join(out,base.replace('/','_')+'.png'));cnt+=1
    elif n.upper().endswith('.NCGR'):
        b=r.files[i];o=0x10;h,w=struct.unpack_from('<HH',b,o+8);bd=struct.unpack_from('<I',b,o+12)[0]
        bpp=4 if bd==3 else 8;dl=struct.unpack_from('<I',b,o+0x18)[0];d=b[o+0x20:o+0x20+dl]
        base=n[:-5];pl=None
        for k in (base+'.NCLR',base+'.nclr'):
            if k in names:pl=r.files[names[k]]
        P=pal(pl[0x28:]) if pl else [(v*16,v*16,v*16) for v in range(256)]
        T=tiles(d,bpp)
        wt=w if 0<w<0xffff and w<=64 else 16
        im=draw(T,P,list(range(len(T))),wt,bpp);im.save(os.path.join(out,base.replace('/','_')+'.png'));cnt+=1
print(cnt)

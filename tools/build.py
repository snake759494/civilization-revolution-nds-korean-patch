"""문명 레볼루션 일본판 한글패치 빌드"""
import sys,json,struct,glob,os,hashlib
sys.path.insert(0,os.path.dirname(__file__))
import ndspy.rom,stbl,bdf
from nftr import NFTR
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
SRC=os.path.join(ROOT,"Sid Meier's Civilization Revolution (Japan).nds")
OUT=os.path.join(ROOT,"Sid Meier's Civilization Revolution (Korean).nds")
W=os.path.join(ROOT,'_work')
def jload(p):return json.load(open(p,encoding='utf8'))
rom=ndspy.rom.NintendoDSRom.fromFile(SRC)
fid=lambda n:rom.filenames.idOf(n)
# 번역 원고
strs=stbl.load(rom.files[fid('Localization/str_JPN.STR')])
tr={}
for p in sorted(glob.glob(os.path.join(W,'translation','str_*.json'))):
    for k,v in jload(p).items():tr[int(k)]=v
txt_tr={}
for p in sorted(glob.glob(os.path.join(W,'translation','txt_*.json'))):txt_tr.update(jload(p))
# 한글 문자 수집 및 코드 배정
texts=list(tr.values())+['제']+[v for d in txt_tr.values() for v in d]
hangul=sorted({c for t in texts for c in t if 0xAC00<=ord(c)<=0xD7A3})
f0=NFTR(rom.files[fid('font/Arial14.nftr')])
slots=sorted(c for c in f0.cmap if c>=0x889f)
assert len(hangul)<=len(slots),(len(hangul),len(slots))
cmap=dict(zip(hangul,slots))
def enc(t):
    out=bytearray()
    for c in t:
        if c in cmap:out+=cmap[c].to_bytes(2,'big')
        else:out+=c.encode('cp932')
    return bytes(out)
# STR
new=[(h,enc(tr[i]) if i in tr else b) for i,(h,b) in enumerate(strs)]
rom.files[fid('Localization/str_JPN.STR')]=stbl.build(rom.files[fid('Localization/str_JPN.STR')],new)
# 이름 txt (원문 줄 순서 유지, 번역 리스트로 교체)
for name,lines in txt_tr.items():
    path='Localization/'+name
    raw=rom.files[fid(path)].decode('cp932').split('\r\n');k=0;res=[]
    for line in raw:
        if line.strip() and not line.startswith(';') and ',' in line:
            nm,rest=line.rsplit(',',1);res.append(lines[k]+','+rest);k+=1
        else:res.append(line)
    assert k==len(lines),(name,k,len(lines))
    rom.files[fid(path)]=enc('\r\n'.join(res))
# ARM9 서수 서식 「第%d」→「제%d」 (같은 길이)
a9=bytearray(rom.arm9);o=0x185230
assert a9[o:o+6]==bytes.fromhex('91e625640000'),a9[o:o+6]
a9[o:o+2]=enc('제');rom.arm9=bytes(a9)
# 폰트: 갈무리11 네이티브 11x11
G=bdf.load(os.path.join(W,'fonts','Galmuri11.bdf'))
for path,top in [('font/Arial14.nftr',1),('Arial14.NFTR',0)]:
    f=NFTR(rom.files[fid(path)])
    for ch,code in cmap.items():
        g=G[ord(ch)];bw,bh,bx,by=g['bbx'];oy=top+11-bh-by;assert bw+bx<=12 and oy>=0 and oy+bh<=f.h,(ch,g['bbx'])
        px=[[0]*f.w for _ in range(f.h)]
        for y,row in enumerate(g['rows']):
            for x in range(bw):
                if row>>(31-x)&1:px[oy+y][bx+x]=1
        gi=f.cmap[code];f.setglyph(gi,px);f.setwidth(gi,(1,11,12))
    rom.files[fid(path)]=bytes(f.d)
os.makedirs(os.path.join(W,'tmp'),exist_ok=True)
json.dump({c:f'{v:04X}' for c,v in cmap.items()},open(os.path.join(W,'tmp','charmap.json'),'w',encoding='utf8'),ensure_ascii=False)
# NDS 배너 제목 (6개 언어 슬롯 모두)
b=bytearray(rom.iconBanner);title=chr(10).join(['시빌라이제이션','레볼루션','사이버프론트']).encode('utf-16le')
for k in range(6):
    o=0x240+k*0x100;b[o:o+0x100]=title.ljust(0x100,bytes(1))
import zlib
def crc16(d):
    c=0xffff
    for x in d:
        c^=x
        for _ in range(8):c=(c>>1)^0xa001 if c&1 else c>>1
    return c
struct.pack_into('<H',b,2,crc16(b[0x20:0x840]))
rom.iconBanner=bytes(b)
rom.saveToFile(OUT)
print('한글',len(hangul),'번역',len(tr),'sha256',hashlib.sha256(open(OUT,'rb').read()).hexdigest())

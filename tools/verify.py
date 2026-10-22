"""빌드 ROM 일본어 잔존 검사: STR·이름 파일·배너"""
import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
import ndspy.rom,stbl
W=os.path.join(os.path.dirname(__file__),'..')
r=ndspy.rom.NintendoDSRom.fromFile(os.path.join(W,'..',"Sid Meier's Civilization Revolution (Korean).nds"))
used={int(v,16) for v in json.load(open(os.path.join(W,'tmp','charmap.json'),encoding='utf8')).values()}
def jp(b):
    i=0;o=[]
    while i<len(b):
        c=b[i]
        if 0x81<=c<=0x9f or 0xe0<=c<=0xfc:
            code=c<<8|b[i+1]
            if code not in used and (0x829f<=code<=0x84be or code>=0x889f):o.append(code)
            i+=2
        elif 0xa1<=c<=0xdf:o.append(c);i+=1
        else:i+=1
    return o
s=stbl.load(r.files[r.filenames.idOf('Localization/str_JPN.STR')])
a=sum(1 for h,x in s if jp(x))
b=sum(len(jp(r.files[i])) for i in range(len(r.files)) if (r.filenames.filenameOf(i) or '').endswith('_JPN.txt'))
t=r.iconBanner[0x240:0x340].decode('utf-16le').rstrip('\0')
kana=any('぀'<=c<='ヿ' for c in t)
print('STR 잔존',a,'이름 파일 잔존',b,'배너',repr(t))
sys.exit(1 if a or b or kana else 0)

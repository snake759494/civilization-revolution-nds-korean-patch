"""번역 묶음 검증: python check.py chunks/src_XX.json chunks/ko_XX.json"""
import sys,json,re,os
sys.path.insert(0,os.path.dirname(__file__));import bdf
G=set(bdf.load(os.path.join(os.path.dirname(__file__),'..','fonts','Galmuri11.bdf')))
src=json.load(open(sys.argv[1],encoding='utf8'));ko=json.load(open(sys.argv[2],encoding='utf8'))
TOK=re.compile(r'@[A-Z_0-9]*?__[A-Z_]+\d|@__NUM\d|%[0-9.*]*[a-z%]')
JP=re.compile(r'[぀-ヿ一-鿿ｦ-ﾟ]')
err=[]
for k,s in src.items():
    if k not in ko:err.append((k,'누락'));continue
    t=ko[k]
    if sorted(TOK.findall(s))!=sorted(TOK.findall(t)):err.append((k,'변수 불일치',TOK.findall(s),TOK.findall(t)))
    if JP.search(t):err.append((k,'일본어 잔존',JP.findall(t)))
    ls=len(s)-len(s.lstrip());lt=len(t)-len(t.lstrip())
    if s[:ls]!=t[:lt] or s[len(s.rstrip()):]!=t[len(t.rstrip()):]:err.append((k,'앞뒤 공백/개행 불일치',repr(s[:ls]+'|'+s[len(s.rstrip()):]),repr(t[:lt]+'|'+t[len(t.rstrip()):])))
    for c in t:
        if 0xAC00<=ord(c)<=0xD7A3:
            if ord(c) not in G:err.append((k,'갈무리에 없는 글자',c))
        else:
            try:c.encode('cp932')
            except:err.append((k,'인코딩 불가 문자',c,hex(ord(c))))
extra=set(ko)-set(src)
if extra:err.append(('추가 키',sorted(extra)[:10]))
for e in err[:80]:print(e)
print('오류',len(err),'/',len(src))

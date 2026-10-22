def load(path):
    g={};cur=None
    for line in open(path,encoding='latin1'):
        p=line.split()
        if not p:continue
        if p[0]=='ENCODING':cur={'cp':int(p[1])}
        elif p[0]=='DWIDTH' and cur is not None:cur['dw']=int(p[1])
        elif p[0]=='BBX' and cur is not None:cur['bbx']=list(map(int,p[1:5]))
        elif p[0]=='BITMAP' and cur is not None:cur['rows']=[]
        elif p[0]=='ENDCHAR' and cur is not None:g[cur['cp']]=cur;cur=None
        elif cur is not None and 'rows' in cur:cur['rows'].append(int(p[0],16)<<(32-len(p[0])*4))
    return g

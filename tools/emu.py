"""사용: python emu.py '<json batch>' | close"""
import sys,json,urllib.request,os
port=json.load(open(os.path.join(os.path.dirname(__file__),'..','runtime','server.json')))['port']
if sys.argv[1]=='close':req=urllib.request.Request(f'http://127.0.0.1:{port}/close',data=b'{}')
else:req=urllib.request.Request(f'http://127.0.0.1:{port}/',data=json.dumps({'batch':json.loads(sys.argv[1])}).encode())
print(urllib.request.urlopen(req,timeout=600).read().decode())

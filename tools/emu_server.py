"""창 없는 DeSmuME 코어 검증 서버 (시스템 키보드/마우스 미사용). POST /close로 종료."""
import sys,json,os,shutil,tempfile
from pathlib import Path
from http.server import HTTPServer,BaseHTTPRequestHandler
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
rom=Path(sys.argv[1]).resolve();out=Path(__file__).resolve().parent.parent/'runtime';out.mkdir(exist_ok=True)
cache=Path(tempfile.gettempdir())/'CivRevKR';cache.mkdir(exist_ok=True);test=cache/'civ.nds';shutil.copyfile(rom,test);os.chdir(cache)
e=DeSmuME();e.volume_set(0);e.open(str(test))
def frames(n):
    for _ in range(n):e.cycle(with_joystick=False)
def act(a):
    if a.get('load_state'):e.savestate.load_file(str(out/a['load_state']))
    mask=0
    for k in a.get('keys','').split('+'):
        if k:mask|=keymask(getattr(Keys,'KEY_'+k.upper()))
    if mask:e.input.keypad_add_key(mask)
    if 'touch' in a:e.input.touch_set_pos(*a['touch'])
    frames(a.get('hold',4 if mask or 'touch' in a else 0))
    if mask:e.input.keypad_rm_key(mask)
    if 'touch' in a:e.input.touch_release()
    frames(a.get('wait',30))
    if a.get('shot'):e.screenshot().save(out/(a['shot']+'.png'))
    if a.get('save_state'):e.savestate.save_file(str(out/a['save_state']))
class H(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def do_POST(self):
        try:
            b=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or '{}')
            if self.path=='/close':
                e.destroy();r={'closed':True};self.send_response(200);self.end_headers();self.wfile.write(b'{"closed":true}');
                import threading;threading.Thread(target=srv.shutdown).start();return
            for a in b.get('batch',[b]):act(a)
            self.send_response(200);self.end_headers();self.wfile.write(b'{"ok":true}')
        except Exception as ex:
            self.send_response(500);self.end_headers();self.wfile.write(repr(ex).encode())
srv=HTTPServer(('127.0.0.1',0),H);(out/'server.json').write_text(json.dumps({'port':srv.server_port}));print('ready',srv.server_port,flush=True)
srv.serve_forever()

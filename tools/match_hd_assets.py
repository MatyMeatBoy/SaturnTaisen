"""Sakura HD matcher: build a local portrait project, review and export a pack."""
import argparse
import io
import json
import os
from pathlib import Path
import secrets
import subprocess
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
import webbrowser
import hd_matching as matching
from hd_matcher_ui import HTML

ROOT=Path(__file__).resolve().parents[1]


def serve(workspace,project,port=8767,open_browser=False):
    root=Path(workspace).resolve();token=secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def respond(self,data,status=200,kind='application/json; charset=utf-8'):
            if isinstance(data,dict):data=json.dumps(data,ensure_ascii=False).encode('utf-8')
            self.send_response(status);self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
        def do_GET(self):
            try:
                path=urlsplit(self.path).path
                if path=='/':return self.respond(HTML.replace('__TOKEN__',json.dumps(token)).encode('utf-8'),kind='text/html; charset=utf-8')
                if path=='/api/project':
                    return self.respond(dict(rows=project['rows'],candidate_count=len(project['candidates'])))
                parts=path.strip('/').split('/')
                if len(parts)!=3 or parts[0]!='image':return self.respond(dict(error='No encontrado'),404)
                _,side,identity=parts;row=next((r for r in project['rows'] if r['id']==identity),None)
                if side=='native' and row:image=matching.load_image(matching.workspace_file(root,row['path']))
                elif side=='pc':
                    candidate=next((c for c in project['candidates'] if str(c['index'])==identity),None)
                    if not candidate:raise ValueError('Candidato no encontrado')
                    image=matching.load_image(matching.workspace_file(root,candidate['path']))
                elif side=='prepared' and row:
                    candidate=next(c for c in project['candidates'] if c['index']==row['selected'])
                    image=matching.prepare_variant(matching.load_image(matching.workspace_file(root,candidate['path'])),
                        matching.workspace_file(root,row['raw']).read_bytes(),2,row['dx'],row['dy'])
                else:raise ValueError('Imagen no encontrada')
                buffer=io.BytesIO();image.save(buffer,format='PNG');self.respond(buffer.getvalue(),kind='image/png')
            except (ValueError,OSError,StopIteration) as error:self.respond(dict(error=str(error)),400)
        def do_POST(self):
            if not secrets.compare_digest(self.headers.get('X-Matcher-Token',''),token):return self.respond(dict(error='Sesión no válida'),403)
            try:
                count=int(self.headers.get('Content-Length','0'))
                if not 0<=count<=4096:raise ValueError('Solicitud demasiado grande')
                request=json.loads(self.rfile.read(count) or b'{}')
                if self.path=='/api/export':return self.respond(matching.export_pack(project,root))
                if self.path!='/api/choose':return self.respond(dict(error='No encontrado'),404)
                row=next((r for r in project['rows'] if r['id']==request.get('id')),None)
                if not row:raise ValueError('Identidad no encontrada')
                if type(request.get('selected')) is not int or request['selected'] not in {c['index'] for c in project['candidates']}:raise ValueError('Candidato inválido')
                if request.get('status') not in ('auto','accepted','pending','rejected'):raise ValueError('Estado inválido')
                for key in ('dx','dy'):
                    if type(request.get(key)) is not int or abs(request[key])>4:raise ValueError('Los ajustes deben ser enteros entre -4 y 4')
                before=row.copy();row.update({k:request[k] for k in ('selected','status','dx','dy')})
                try:matching.atomic_json(root/'project.json',project)
                except OSError:row.clear();row.update(before);raise
                self.respond(dict(saved=True))
            except (ValueError,OSError,TypeError) as error:self.respond(dict(error=str(error)),400)
    try:server=HTTPServer(('127.0.0.1',port),Handler)
    except OSError:server=HTTPServer(('127.0.0.1',0),Handler)
    url=f'http://127.0.0.1:{server.server_port}'
    print(url,flush=True)
    if open_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,default=ROOT/'local/work/hd-matcher-project')
    parser.add_argument('--output',type=Path,help='destination mod directory; only used when exporting')
    parser.add_argument('--prepare',action='store_true',help='rebuild candidates; preserves an existing review project')
    parser.add_argument('--serve',action='store_true')
    parser.add_argument('--open',action='store_true')
    parser.add_argument('--export',action='store_true')
    parser.add_argument('--port',type=int,default=8767)
    parser.add_argument('--disc',type=Path,action='append')
    parser.add_argument('--state',type=Path,default=ROOT/'local/work/sakura/iris-correct-room-3000.state')
    parser.add_argument('--palette-bank',type=int,default=4)
    parser.add_argument('--pc-root',type=Path,default=ROOT/'local/work/v02-pc-game/_t_@_C__')
    parser.add_argument('--runtime',type=Path,default=ROOT/'local/build/sakura/sakura.exe')
    args=parser.parse_args();workspace=args.workspace.resolve();workspace.mkdir(parents=True,exist_ok=True)
    path=workspace/'project.json'
    if args.prepare or not path.is_file():
        if path.is_file():
            backup=workspace/('project-before-'+str(os.stat(path).st_mtime_ns)+'.json')
            backup.write_bytes(path.read_bytes())
        source=args.pc_root/'SAKURA1/SYSTEM/KAO.SPR'
        if not source.is_file() or not args.runtime.is_file():parser.error('Falta KAO.SPR extraído o el runtime de desarrollo')
        decoded=workspace/('decoded-'+matching.fingerprint(source)[:16]);decoded.mkdir(exist_ok=True)
        if len(list(decoded.glob('KAO-*.png')))!=394:
            env=os.environ.copy();env['PATH']='C:/msys64/clang64/bin;'+env.get('PATH','')
            print('Decodificando recursos PC propios…',flush=True)
            subprocess.run([str(args.runtime),'--export-pc-spr',str(source.resolve()),str(decoded)],env=env,check=True,capture_output=True,timeout=60)
        print('Comparando retratos de ambos discos…',flush=True)
        project=matching.prepare_fce_project(args.disc or [ROOT/'local/prepared/disc1/Track 01.iso',ROOT/'local/prepared/disc2/Track 01.iso'],
            args.state,args.palette_bank,decoded,source,workspace,args.output or ROOT/'local/profiles/v02-dev/mods/hd-portraits')
    else:
        if path.stat().st_size>4*1024*1024:parser.error('Proyecto demasiado grande')
        project=json.loads(path.read_text(encoding='utf-8'))
        if project.get('schema')!=1 or project.get('kind')!='sakura-narrative-portraits':parser.error('Proyecto incompatible')
    if args.output:
        project['output']=str(args.output.resolve());matching.atomic_json(path,project)
    print(f"{len(project['rows'])} retratos; {sum(r['status']=='auto' for r in project['rows'])} preseleccionados",flush=True)
    if args.export:print(json.dumps(matching.export_pack(project,workspace),indent=2))
    if args.serve:serve(workspace,project,args.port,args.open)


if __name__=='__main__':main()

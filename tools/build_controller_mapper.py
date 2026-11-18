"""Build a portable raw controller reporter; no game inputs are required."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
TC=Path('C:/msys64/clang64')

def main():
    imgui=ROOT/'local/build/launcher/_deps/imgui-src'
    if not (imgui/'imgui.cpp').is_file():
        raise RuntimeError('Build the project launcher first to fetch its pinned ImGui dependency')
    destination=ROOT/'local/build/controller-mapper';destination.mkdir(parents=True,exist_ok=True)
    exe=destination/'Mapear M30.exe'
    sources=[ROOT/'tools/controller_mapper.cpp']+[imgui/name for name in ('imgui.cpp','imgui_draw.cpp','imgui_tables.cpp','imgui_widgets.cpp','backends/imgui_impl_sdl3.cpp','backends/imgui_impl_sdlrenderer3.cpp')]
    env=os.environ.copy();env['PATH']=str(TC/'bin')+os.pathsep+env.get('PATH','')
    subprocess.run([str(TC/'bin/clang++.exe'),'-std=c++20','-O2','-mwindows',*map(str,sources),'-I',str(imgui),'-I',str(imgui/'backends'),'-I',str(TC/'include'),'-L',str(TC/'lib'),'-lSDL3','-o',str(exe)],env=env,check=True)
    available={p.name.casefold():p for p in (TC/'bin').glob('*.dll')};seen=set();pending=[exe]
    system=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32'
    while pending:
        output=subprocess.check_output([str(TC/'bin/llvm-readobj.exe'),'--coff-imports',str(pending.pop())],env=env,text=True)
        for name in re.findall(r'^\s+Name: ([^\r\n]+\.dll)\s*$',output,re.MULTILINE|re.IGNORECASE):
            key=name.casefold()
            if key in seen:continue
            seen.add(key)
            if key in available:
                target=destination/available[key].name;shutil.copy2(available[key],target);pending.append(target)
            elif not (system/name).is_file() and not key.startswith(('api-ms-','ext-ms-')):
                raise RuntimeError('Unresolved DLL: '+name)
    (destination/'LEEME.txt').write_text('MAPEADOR DE MANDOS - SaturnTaisenFirst\n\nAbre Mapear M30.exe, selecciona tu mando y su modo de conexion. Deja todo en reposo y pulsa Comenzar. Pulsa el boton resaltado en el esquema y sueltalo antes de continuar. Puedes repetir u omitir pasos. Back/Select es extra de PC: Saturn no tenia ese boton.\n\nAl terminar, pulsa Guardar informe y envia el JSON del directorio informes al chat. El programa no aplica bindings ni envia informacion por Internet. Si no puede escribir junto al EXE usara AppData y mostrara la ruta.\n\nIncluye esquemas Saturn, Genesis 3 botones y Genesis 6 botones. Para comparar modos Bluetooth/XInput/DInput/2.4G, crea un informe nuevo en cada modo que quieras probar. No necesita los juegos, Python, compiladores ni instalacion.\n',encoding='utf-8')
    licenses=destination/'licenses';licenses.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'LICENSE',licenses/'SaturnTaisenFirst-GPL-3.0.txt')
    shutil.copy2(imgui/'LICENSE.txt',licenses/'Dear-ImGui.txt')
    for package in ('SDL3','libc++','libc++abi','libunwind'):
        source=TC/'share/licenses'/package
        if source.is_dir():shutil.copytree(source,licenses/package,dirs_exist_ok=True)
    manifest=dict(tool='Controller Mapper 1',game_inputs_required=False,network_upload=False,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'tools/controller_mapper.cpp',ROOT/'tools/controller_capture.h',Path(__file__))},
        files=[dict(path=p.relative_to(destination).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(destination.rglob('*')) if p.is_file() and (p==exe or p.suffix=='.dll' or p.name=='LEEME.txt' or licenses in p.parents)])
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(exe)

if __name__=='__main__':main()

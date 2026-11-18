// SPDX-License-Identifier: GPL-3.0-only
// Raw controller calibration. It never changes the game's bindings.
#include "controller_capture.h"
#include <SDL3/SDL.h>
#include <imgui.h>
#include <imgui_impl_sdl3.h>
#include <imgui_impl_sdlrenderer3.h>
#include <array>
#include <chrono>
#include <cmath>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <memory>
#include <sstream>

using namespace controller_capture;
namespace {
struct Identity {std::string name,guid;unsigned vid=0,pid=0;};
Identity Identify(SDL_Joystick* joystick) {
    char guid[33];SDL_GUIDToString(SDL_GetJoystickGUID(joystick),guid,sizeof(guid));
    const char* name=SDL_GetJoystickName(joystick);
    return {name?name:"Desconocido",guid,SDL_GetJoystickVendor(joystick),SDL_GetJoystickProduct(joystick)};
}
const char* Label(const std::string& action) {
    if(action=="up")return "Cruceta arriba";
    if(action=="down")return "Cruceta abajo";
    if(action=="left")return "Cruceta izquierda";
    if(action=="right")return "Cruceta derecha";
    if(action=="start")return "Start";
    if(action=="select")return "Back / Select (extra de PC)";
    static const char* letters[]={"A","B","C","X","Y","Z","L","R"};
    static const char* names[]={"a","b","c","x","y","z","l","r"};
    for(int i=0;i<8;i++)if(action==names[i])return letters[i];
    return "";
}
std::string Hex(unsigned value) {std::ostringstream text;text<<std::hex<<std::uppercase<<std::setfill('0')<<std::setw(4)<<value;return text.str();}
void Diagram(Session& session,Layout layout) {
    const auto origin=ImGui::GetCursorScreenPos();
    const float scale=std::min(1.15f,ImGui::GetContentRegionAvail().x/740.0f);
    const float left=(ImGui::GetContentRegionAvail().x-700*scale)*.5f;
    auto p=[&](float x,float y){return ImVec2(origin.x+left+x*scale,origin.y+y*scale);};
    auto* d=ImGui::GetWindowDrawList();
    const auto shell=IM_COL32(62,57,71,255),trim=IM_COL32(93,82,101,255),base=IM_COL32(110,99,120,255);
    const auto current=session.complete()?std::string():session.actions()[session.index()];
    d->AddCircleFilled(p(150,200),110*scale,shell,64);d->AddCircleFilled(p(550,200),110*scale,shell,64);
    d->AddRectFilled(p(145,90),p(555,290),shell,35*scale);
    d->AddRect(p(115,105),p(585,280),trim,45*scale,0,2*scale);
    auto done=[&](const std::string& action) {
        for(size_t i=0;i<session.index();i++)if(session.actions()[i]==action)return session.bindings()[i].kind!=Kind::None;
        return false;
    };
    auto color=[&](const std::string& a){return current==a?IM_COL32(223,93,139,255):done(a)?IM_COL32(78,144,117,255):base;};
    auto label=[&](ImVec2 centre,const char* text) {
        auto size=ImGui::CalcTextSize(text);d->AddText({centre.x-size.x*.5f,centre.y-size.y*.5f},IM_COL32_WHITE,text);
    };
    auto key=[&](const char* a,float x,float y,float radius) {
        d->AddCircleFilled(p(x+2,y+4),radius*scale,IM_COL32(28,24,35,255),36);
        d->AddCircleFilled(p(x,y),radius*scale,color(a),36);label(p(x,y),Label(a));
    };
    auto direction=[&](const char* a,float x,float y,const char* text) {
        d->AddRectFilled(p(x-19,y-19),p(x+19,y+19),color(a),5*scale);label(p(x,y),text);
    };
    direction("up",160,153,"↑");direction("down",160,229,"↓");
    direction("left",122,191,"←");direction("right",198,191,"→");
    d->AddRectFilled(p(141,172),p(179,210),base,4*scale);
    key("a",429,220,28);key("b",500,203,28);key("c",570,186,28);
    if(layout!=Layout::Genesis3){key("x",425,149,21);key("y",491,132,21);key("z",557,115,21);}
    d->AddRectFilled(p(290,184),p(350,210),color("start"),12*scale);label(p(320,197),"Start");
    if(layout==Layout::Saturn) {
        d->AddRectFilled(p(104,73),p(235,100),color("l"),10*scale);label(p(168,86),"L");
        d->AddRectFilled(p(455,60),p(586,87),color("r"),10*scale);label(p(520,73),"R");
        d->AddRectFilled(p(290,235),p(350,258),color("select"),10*scale);label(p(320,247),"Back");
    }
    ImGui::Dummy({700*scale,325*scale});
}
bool Neutral(SDL_Joystick* joystick,const std::vector<int>& rest) {
    for(int i=0;i<SDL_GetNumJoystickButtons(joystick);i++)if(SDL_GetJoystickButton(joystick,i))return false;
    for(int i=0;i<SDL_GetNumJoystickHats(joystick);i++)if(SDL_GetJoystickHat(joystick,i))return false;
    for(size_t i=0;i<rest.size();i++)if(std::abs(int(SDL_GetJoystickAxis(joystick,int(i)))-rest[i])>10000)return false;
    return true;
}
std::filesystem::path SaveReport(const Session& session,const Identity& identity,const std::string& mapping,const std::string& mode,std::string& error) {
    const auto json=session.json(identity.name,identity.guid,identity.vid,identity.pid,mapping,mode);
    const auto time=std::time(nullptr);std::tm stamp{};
#ifdef _WIN32
    gmtime_s(&stamp,&time);
#else
    gmtime_r(&time,&stamp);
#endif
    std::ostringstream filename;filename<<"mando-"<<std::put_time(&stamp,"%Y%m%d-%H%M%S")<<'-'<<SDL_GetTicks()<<".json";
    std::vector<std::filesystem::path> roots{std::filesystem::u8path(SDL_GetBasePath())/"informes"};
    if(char* fallback=SDL_GetPrefPath("MatyMeatBoy","ControllerMapper")) {roots.push_back(std::filesystem::u8path(fallback)/"informes");SDL_free(fallback);}
    for(const auto& root:roots) {
        std::error_code ec;std::filesystem::create_directories(root,ec);if(ec)continue;
        auto file=root/filename.str();auto temporary=file;temporary+=".tmp";
        if(std::filesystem::exists(file) || std::filesystem::exists(temporary))continue;
        {std::ofstream output(temporary,std::ios::binary);if(!output)continue;output<<json;output.close();if(!output) {std::filesystem::remove(temporary,ec);continue;}}
        std::filesystem::rename(temporary,file,ec);if(!ec)return file;
        std::filesystem::remove(temporary,ec);
    }
    error="No se pudo guardar el informe. Revisa el permiso de escritura de la carpeta.";return {};
}
}
int main(int argc,char** argv) {
    const bool uiTest=argc>1 && std::string(argv[1])=="--test-ui";
    const bool virtualTest=argc>1 && std::string(argv[1])=="--test-virtual";
    const bool diagnostic=uiTest || virtualTest;
    if(virtualTest)SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS,"1");
    if(!SDL_Init(SDL_INIT_VIDEO|SDL_INIT_JOYSTICK|SDL_INIT_GAMEPAD))return 1;
    SDL_Window* window=SDL_CreateWindow("SaturnTaisenFirst · Mapeador de mandos",1040,900,SDL_WINDOW_RESIZABLE|(diagnostic?SDL_WINDOW_HIDDEN:0));
    if(!window){SDL_Quit();return 1;}
    SDL_SetWindowMinimumSize(window,820,760);
    SDL_Renderer* renderer=SDL_CreateRenderer(window,nullptr);
    if(!renderer){SDL_DestroyWindow(window);SDL_Quit();return 1;}
    SDL_SetRenderVSync(renderer,1);
    ImGui::CreateContext();auto& io=ImGui::GetIO();io.IniFilename=nullptr;
    if(const char* windows=getenv("WINDIR")) {
        const auto font=std::filesystem::path(windows)/"Fonts/segoeui.ttf";
        if(std::filesystem::is_regular_file(font))io.Fonts->AddFontFromFileTTF(font.string().c_str(),20);
    }
    ImGui::StyleColorsLight();auto& style=ImGui::GetStyle();
    style.WindowRounding=24;style.FrameRounding=10;style.ChildRounding=16;style.ItemSpacing={12,10};style.FramePadding={14,9};style.WindowPadding={28,22};
    style.Colors[ImGuiCol_WindowBg]={.98f,.94f,.93f,1};style.Colors[ImGuiCol_FrameBg]={1,.98f,.98f,1};
    style.Colors[ImGuiCol_Button]={.89f,.72f,.77f,1};style.Colors[ImGuiCol_ButtonHovered]={.94f,.64f,.74f,1};style.Colors[ImGuiCol_ButtonActive]={.83f,.44f,.59f,1};
    style.Colors[ImGuiCol_Header]={.90f,.69f,.77f,1};style.Colors[ImGuiCol_Text]={.22f,.17f,.23f,1};
    if(!ImGui_ImplSDL3_InitForSDLRenderer(window,renderer) || !ImGui_ImplSDLRenderer3_Init(renderer))return 2;
    SDL_Joystick* joystick=nullptr;SDL_JoystickID selected=0;
    Identity identity;
    std::vector<int> rest;std::string mapping,status,lastInput;std::filesystem::path saved;
    int layoutIndex=0,modeIndex=0;Session session(Layout::Saturn);bool learning=false,running=true;
    uint64_t acceptAfter=0;unsigned passes=0;
    const char* modes[]={"No sé / automático","Bluetooth","USB directo","Receptor 2.4G","XInput","DInput","Switch"};
    const char* layouts[]={"Saturn · 6 botones + L/R","Mega Drive / Genesis · 3 botones","Mega Drive / Genesis · 6 botones"};
    SDL_JoystickID virtualId=0;int heldButton=-1;bool heldHat=false;uint64_t pressedAt=0;
    if(virtualTest) {
        SDL_VirtualJoystickDesc desc;SDL_INIT_INTERFACE(&desc);
        desc.type=SDL_JOYSTICK_TYPE_GAMEPAD;desc.vendor_id=0x2dc8;desc.product_id=0x5006;
        desc.naxes=2;desc.nbuttons=16;desc.nhats=1;desc.name="SDL virtual calibration test (not physical)";
        virtualId=SDL_AttachVirtualJoystick(&desc);selected=virtualId;joystick=SDL_OpenJoystick(selected);
        if(!joystick)return 3;
        identity=Identify(joystick);rest.assign(2,0);learning=true;acceptAfter=SDL_GetTicks()+100;
    }
    while(running) {
        const auto now=SDL_GetTicks();SDL_Event event;
        while(SDL_PollEvent(&event)) {
            ImGui_ImplSDL3_ProcessEvent(&event);
            if(event.type==SDL_EVENT_QUIT)running=false;
            if(event.type==SDL_EVENT_JOYSTICK_REMOVED && event.jdevice.which==selected) {
                if(joystick)SDL_CloseJoystick(joystick);joystick=nullptr;selected=0;learning=false;status="Mando desconectado. Reconéctalo y selecciónalo de nuevo.";
            }
            Binding input;bool relevant=false;
            if(event.type==SDL_EVENT_JOYSTICK_BUTTON_DOWN && event.jbutton.which==selected) {input={Kind::Button,event.jbutton.button,1,0};relevant=true;}
            if(event.type==SDL_EVENT_JOYSTICK_HAT_MOTION && event.jhat.which==selected && event.jhat.value) {input={Kind::Hat,event.jhat.hat,event.jhat.value,0};relevant=true;}
            if(event.type==SDL_EVENT_JOYSTICK_AXIS_MOTION && event.jaxis.which==selected && event.jaxis.axis<rest.size()) {
                const int delta=int(event.jaxis.value)-rest[event.jaxis.axis];
                if(std::abs(delta)>16000) {input={Kind::Axis,event.jaxis.axis,delta>0?1:-1,rest[event.jaxis.axis]};relevant=true;}
            }
            if(relevant) {
                lastInput=Describe(input);
                if(learning && now>=acceptAfter && (diagnostic || (SDL_GetWindowFlags(window)&SDL_WINDOW_INPUT_FOCUS)) && session.accept(input))acceptAfter=now+350;
            }
        }
        if(joystick && learning && now>=acceptAfter && Neutral(joystick,rest))session.release();
        if(virtualTest) {
            if((heldButton>=0 || heldHat) && now>=pressedAt+80) {
                if(heldButton>=0)SDL_SetJoystickVirtualButton(joystick,heldButton,false);
                if(heldHat)SDL_SetJoystickVirtualHat(joystick,0,0);
                heldButton=-1;heldHat=false;
            }else if(heldButton<0 && !heldHat && session.armed() && !session.complete() && now>=acceptAfter) {
                if(session.index()<4) {
                    constexpr Uint8 hats[]={SDL_HAT_UP,SDL_HAT_DOWN,SDL_HAT_LEFT,SDL_HAT_RIGHT};
                    SDL_SetJoystickVirtualHat(joystick,0,hats[session.index()]);heldHat=true;
                }else {heldButton=int(session.index());SDL_SetJoystickVirtualButton(joystick,heldButton,true);}
                pressedAt=now;
            }
            if(session.complete() && heldButton<0 && !heldHat && saved.empty())saved=SaveReport(session,identity,mapping,"virtual regression only",status);
            if(now>20000)running=false;
        }
        ImGui_ImplSDLRenderer3_NewFrame();ImGui_ImplSDL3_NewFrame();ImGui::NewFrame();
        ImGui::SetNextWindowPos({0,0});ImGui::SetNextWindowSize(io.DisplaySize);
        ImGui::Begin("Mapeador",nullptr,ImGuiWindowFlags_NoDecoration|ImGuiWindowFlags_NoSavedSettings);
        ImGui::TextColored({.63f,.24f,.40f,1},"SATURN TAISEN FIRST  /  HERRAMIENTAS");
        ImGui::TextUnformatted("Tu mando, botón por botón");
        ImGui::TextWrapped("Pulsa el botón físico resaltado. El informe registra entradas reales; no cambia la configuración del juego.");
        ImGui::Separator();
        int count=0;SDL_JoystickID* devices=SDL_GetJoysticks(&count);
        ImGui::SetNextItemWidth(-1);
        if(ImGui::BeginCombo("##device",joystick?SDL_GetJoystickName(joystick):"Selecciona tu mando conectado")) {
            for(int i=0;i<count;i++) {
                const char* name=SDL_GetJoystickNameForID(devices[i]);std::string label=std::string(name?name:"Mando")+"##"+std::to_string(devices[i]);
                if(ImGui::Selectable(label.c_str(),selected==devices[i])) {
                    if(joystick)SDL_CloseJoystick(joystick);
                    selected=devices[i];joystick=SDL_OpenJoystick(selected);learning=false;session=Session(static_cast<Layout>(layoutIndex));saved.clear();status.clear();
                    rest.clear();mapping.clear();
                    if(joystick) {
                        identity=Identify(joystick);
                        for(int j=0;j<SDL_GetNumJoystickAxes(joystick);j++)rest.push_back(SDL_GetJoystickAxis(joystick,j));
                        if(char* value=SDL_GetGamepadMappingForID(selected)){mapping=value;SDL_free(value);}
                    }else {selected=0;status=SDL_GetError();}
                }
            }
            ImGui::EndCombo();
        }
        SDL_free(devices);
        if(!count)ImGui::TextWrapped("No hay mandos conectados. Conecta el M30 por Bluetooth, USB o su receptor.");
        if(ImGui::BeginTable("Disposición",2,ImGuiTableFlags_SizingStretchSame)) {
            ImGui::TableNextColumn();ImGui::TextUnformatted("Esquema");ImGui::SetNextItemWidth(-1);
            if(ImGui::Combo("##layout",&layoutIndex,layouts,3)){session=Session(static_cast<Layout>(layoutIndex));learning=false;saved.clear();}
            ImGui::TableNextColumn();ImGui::TextUnformatted("Modo de conexión");ImGui::SetNextItemWidth(-1);ImGui::Combo("##mode",&modeIndex,modes,7);ImGui::EndTable();
        }
        if(joystick) {
            ImGui::Text("VID %s   PID %s   %d botones · %d ejes · %d crucetas",Hex(SDL_GetJoystickVendor(joystick)).c_str(),Hex(SDL_GetJoystickProduct(joystick)).c_str(),SDL_GetNumJoystickButtons(joystick),SDL_GetNumJoystickAxes(joystick),SDL_GetNumJoystickHats(joystick));
        }
        if(learning && !session.complete()) {
            ImGui::TextColored({.64f,.22f,.39f,1},"%zu / %zu   Pulsa: %s",session.index()+1,session.actions().size(),Label(session.actions()[session.index()]));
            if(!session.armed())ImGui::TextUnformatted("Suelta todos los botones y deja los ejes en reposo antes del siguiente paso.");
        }else if(session.complete())ImGui::TextUnformatted("Recorrido terminado. Revisa las asignaciones y guarda el informe.");
        else ImGui::TextUnformatted("Deja el mando en reposo y pulsa Comenzar. El botón Back es opcional: no existía en Saturn.");
        Diagram(session,static_cast<Layout>(layoutIndex));
        ImGui::BeginDisabled(!joystick);
        if(ImGui::Button(learning?"Volver a empezar":"Comenzar",{210,42})) {
            session=Session(static_cast<Layout>(layoutIndex));learning=true;saved.clear();status.clear();
            for(size_t i=0;i<rest.size();i++)rest[i]=SDL_GetJoystickAxis(joystick,int(i));acceptAfter=now+600;
        }
        ImGui::SameLine();
        ImGui::BeginDisabled(!learning || session.index()==0);if(ImGui::Button("Repetir anterior",{170,42})){session.back();acceptAfter=now+400;}ImGui::EndDisabled();
        ImGui::SameLine();ImGui::BeginDisabled(!learning || session.complete());if(ImGui::Button("Omitir",{110,42})){session.skip();acceptAfter=now+400;}ImGui::EndDisabled();
        ImGui::EndDisabled();
        ImGui::SameLine();ImGui::BeginDisabled(!session.complete() || identity.guid.empty());
        if(ImGui::Button("Guardar informe",{190,42})) {saved=SaveReport(session,identity,mapping,modes[modeIndex],status);if(!saved.empty()){status="Informe guardado. Compártelo en el chat para ajustar el perfil.";ImGui::OpenPopup("Informe guardado");}}
        ImGui::EndDisabled();
        if(ImGui::BeginPopupModal("Informe guardado",nullptr,ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::TextUnformatted("Tu mapeo está guardado. Este es el JSON para el diagnóstico:");
            const auto raw=saved.u8string();const std::string path(raw.begin(),raw.end());
            ImGui::PushTextWrapPos(ImGui::GetCursorPosX()+620);ImGui::TextUnformatted(path.c_str());ImGui::PopTextWrapPos();
            if(ImGui::Button("Copiar ruta"))SDL_SetClipboardText(path.c_str());
            ImGui::SameLine();if(ImGui::Button("Cerrar"))ImGui::CloseCurrentPopup();
            ImGui::EndPopup();
        }
        if(!session.error().empty())ImGui::TextWrapped("%s",session.error().c_str());
        if(!lastInput.empty())ImGui::Text("Última entrada: %s",lastInput.c_str());
        ImGui::BeginChild("Asignaciones",{0,150},ImGuiChildFlags_Borders);
        if(ImGui::BeginTable("bindings",4,ImGuiTableFlags_SizingStretchProp)) {
            for(size_t i=0;i<session.actions().size();i++) {
                if(i%2==0)ImGui::TableNextRow();ImGui::TableNextColumn();ImGui::TextUnformatted(Label(session.actions()[i]));
                ImGui::TableNextColumn();ImGui::TextUnformatted(Describe(session.bindings()[i]).c_str());
            }ImGui::EndTable();
        }ImGui::EndChild();
        if(!status.empty())ImGui::TextWrapped("%s",status.c_str());
        if(!saved.empty()) {
            const auto raw=saved.u8string();const std::string path(raw.begin(),raw.end());
            ImGui::TextWrapped("%s",path.c_str());
            if(ImGui::Button("Copiar ruta del informe"))SDL_SetClipboardText(path.c_str());
        }
        ImGui::End();ImGui::Render();
        SDL_SetRenderDrawColor(renderer,249,237,234,255);SDL_RenderClear(renderer);
        ImGui_ImplSDLRenderer3_RenderDrawData(ImGui::GetDrawData(),renderer);
        if((diagnostic && passes==5) || (virtualTest && !saved.empty())) {
            if(auto* image=SDL_RenderReadPixels(renderer,nullptr)) {SDL_SavePNG(image,"mapper-preview.png");SDL_DestroySurface(image);}
        }
        SDL_RenderPresent(renderer);
        ++passes;
        if(uiTest && passes>=8)running=false;
        if(virtualTest && !saved.empty())running=false;
        SDL_Delay(8);
    }
    if(joystick)SDL_CloseJoystick(joystick);
    if(virtualId)SDL_DetachVirtualJoystick(virtualId);
    ImGui_ImplSDLRenderer3_Shutdown();ImGui_ImplSDL3_Shutdown();ImGui::DestroyContext();
    SDL_DestroyRenderer(renderer);SDL_DestroyWindow(window);SDL_Quit();return virtualTest && saved.empty()?4:0;
}

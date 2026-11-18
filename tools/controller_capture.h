// SPDX-License-Identifier: GPL-3.0-only
#pragma once
#include <algorithm>
#include <string>
#include <vector>
namespace controller_capture {
enum class Layout {Saturn,Genesis3,Genesis6};
enum class Kind {None,Button,Axis,Hat};
struct Binding {
    Kind kind=Kind::None;
    int index=0,value=0,rest=0;
    bool operator==(const Binding&) const = default;
};
inline std::string Escape(const std::string& text) {
    std::string out;
    constexpr char hex[]="0123456789abcdef";
    for(unsigned char c:text) {
        switch(c) {
            case '"':out+="\\\"";break;
            case '\\':out+="\\\\";break;
            case '\n':out+="\\n";break;
            case '\r':out+="\\r";break;
            case '\t':out+="\\t";break;
            default:if(c<32) {out+="\\u00";out+=hex[c>>4];out+=hex[c&15];}else out+=char(c);
        }
    }
    return out;
}
inline const char* LayoutName(Layout layout) {
    return layout==Layout::Saturn?"saturn":layout==Layout::Genesis3?"genesis_3":"genesis_6";
}
inline const char* KindName(Kind kind) {
    switch(kind) {case Kind::Button:return "button";case Kind::Axis:return "axis";case Kind::Hat:return "hat";default:return "none";}
}
inline std::string Describe(const Binding& b) {
    if(b.kind==Kind::None)return "Sin asignar";
    if(b.kind==Kind::Button)return "Botón físico "+std::to_string(b.index);
    if(b.kind==Kind::Hat)return "Cruceta "+std::to_string(b.index)+" / máscara "+std::to_string(b.value);
    return "Eje "+std::to_string(b.index)+(b.value>0?" +":" −")+" (reposo "+std::to_string(b.rest)+")";
}
class Session {
    Layout layout_;
    std::vector<std::string> actions_;
    std::vector<Binding> bindings_;
    size_t index_=0;
    bool armed_=false;
    std::string error_;
public:
    explicit Session(Layout layout):layout_(layout),actions_{"up","down","left","right","a","b","c"} {
        if(layout!=Layout::Genesis3)actions_.insert(actions_.end(),{"x","y","z"});
        if(layout==Layout::Saturn)actions_.insert(actions_.end(),{"l","r"});
        actions_.push_back("start");
        if(layout==Layout::Saturn)actions_.push_back("select");
        bindings_.resize(actions_.size());
    }
    const auto& actions() const {return actions_;}
    const auto& bindings() const {return bindings_;}
    size_t index() const {return index_;}
    bool complete() const {return index_==actions_.size();}
    bool armed() const {return armed_;}
    const std::string& error() const {return error_;}
    void release(){armed_=true;}
    void back() {if(index_) {--index_;bindings_[index_]={};}armed_=false;error_.clear();}
    void skip() {if(!complete()) {bindings_[index_++]={};armed_=false;error_.clear();}}
    bool accept(Binding binding) {
        if(complete() || !armed_)return false;
        if(binding.index<0 || binding.index>255 || binding.kind==Kind::None ||
           (binding.kind==Kind::Hat && binding.value!=1 && binding.value!=2 && binding.value!=4 && binding.value!=8) ||
           (binding.kind==Kind::Axis && binding.value!=1 && binding.value!=-1))return false;
        if(std::find(bindings_.begin(),bindings_.begin()+index_,binding)!=bindings_.begin()+index_) {
            error_="Esa entrada ya está asignada. Suelta el mando y pulsa el botón indicado.";
            return false;
        }
        bindings_[index_++]=binding;armed_=false;error_.clear();return true;
    }
    std::string json(const std::string& name,const std::string& guid,unsigned vid,unsigned pid,
                     const std::string& mapping,const std::string& transport) const {
        std::string out="{\n\"schema\":1,\"tool\":\"SaturnTaisenFirst Controller Mapper 1\",\"layout\":\"";
        out+=LayoutName(layout_);
        out+="\",\"input_layer\":\"SDL3 raw joystick\",\n\"device\":{\"name\":\""+Escape(name)+"\",\"guid\":\""+Escape(guid)+
            "\",\"vendor_id\":"+std::to_string(vid)+",\"product_id\":"+std::to_string(pid)+"},\n\"transport_note\":\""+Escape(transport)+
            "\",\n\"existing_sdl_mapping\":\""+Escape(mapping)+"\",\n\"all_steps_visited\":"+(complete()?"true":"false")+",\n\"actions\":[\n";
        for(size_t i=0;i<actions_.size();i++) {
            const auto& b=bindings_[i];
            if(i)out+=",\n";
            out+="{\"action\":\""+actions_[i]+"\",\"kind\":\""+KindName(b.kind)+"\",\"index\":"+std::to_string(b.index)+
                ",\"value\":"+std::to_string(b.value)+",\"rest\":"+std::to_string(b.rest)+"}";
        }
        return out+"\n]}\n";
    }
};
}

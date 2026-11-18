#include "controller_capture.h"
#include <cassert>
#include <string>
int main() {
    using namespace controller_capture;
    Session s(Layout::Saturn);
    assert(s.actions().size()==14 && s.actions()[4]=="a");
    Binding button{Kind::Button,2,1,0};
    assert(!s.accept(button)); // release gate has not been armed
    s.release();assert(s.accept(button));
    assert(!s.accept(Binding{Kind::Button,3,1,0})); // one press cannot fill two prompts
    s.release();assert(!s.accept(button)); // duplicate physical binding rejected
    assert(s.index()==1);
    assert(!s.accept(Binding{Kind::Hat,0,3,0})); // a diagonal is not a direction
    assert(s.accept(Binding{Kind::Hat,0,2,0}));
    s.back();assert(s.index()==1);s.release();
    assert(s.accept(Binding{Kind::Axis,1,-1,0}));
    s.release();assert(s.accept(Binding{Kind::Axis,1,1,0})); // opposite half-axis is distinct
    while(!s.complete()){s.skip();}
    auto json=s.json("M30 \"BT\"", "guid", 0x2dc8, 0x5006, "existing\\mapping\n", "Bluetooth");
    assert(json.find("M30 \\\"BT\\\"")!=std::string::npos);
    assert(json.find("\"layout\":\"saturn\"")!=std::string::npos);
    assert(json.find("\"rest\":0")!=std::string::npos);
    assert(json.find("\"kind\":\"none\"")!=std::string::npos);
    Session three(Layout::Genesis3),six(Layout::Genesis6);
    assert(three.actions().size()==8 && six.actions().size()==11);
    assert(three.actions()[4]=="a" && three.actions().back()=="start");
    assert(Escape("one\ttwo\r\n")=="one\\ttwo\\r\\n");
}

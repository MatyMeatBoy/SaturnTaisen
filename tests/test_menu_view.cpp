#include "menu.h"
#include <cassert>
int main() {
    recomp::Menu menu;
    recomp::MenuConfig config;
    config.groups={{{recomp::MenuRow::Save},{recomp::MenuRow::Load},{recomp::MenuRow::Slot},{recomp::MenuRow::Resume}}};
    menu.Configure(config); menu.Open();
    auto view=menu.View(); assert(view.items.size()==4 && view.selected==0);
    menu.Select(2); assert(menu.View().selected==2);
    menu.Buttons(recomp::kMenuRight); assert(menu.Slot()==2);
    assert(menu.View().items[2].value=="2");
    menu.Select(999); assert(menu.View().selected==3);
    menu.Select(-1); assert(menu.View().selected==0);
    menu.Select(1); auto chosen=menu.Buttons(recomp::kMenuConfirm);
    assert(chosen.kind==recomp::Menu::Chosen::Load && menu.IsOpen());
    menu.Select(3); menu.Buttons(recomp::kMenuConfirm); assert(!menu.IsOpen());
}

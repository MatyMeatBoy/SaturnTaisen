#include "controller_profiles.h"
#include <cassert>
int main() {
    using namespace port;
    assert(IdentifySaturnPad(0x2dc8,0x5006,"Bluetooth Wireless Controller")==SaturnPadProfile::M30);
    assert(IdentifySaturnPad(0x2dc8,0x0651,"Bluetooth Wireless Controller")==SaturnPadProfile::M30);
    assert(IdentifySaturnPad(0x0ca3,0x0024,"6B controller")==SaturnPadProfile::M30);
    assert(IdentifySaturnPad(0,0,"8BitDo M30 2.4G Gamepad")==SaturnPadProfile::M30);
    assert(IdentifySaturnPad(0x045e,0x028e,"Xbox 360 Controller")==SaturnPadProfile::Standard);
    assert(ChooseSaturnProfile(0x045e,0x028e,"Xbox 360 Controller","m30")==SaturnPadProfile::M30);
    assert(ChooseSaturnProfile(0x045e,0x028e,"Xbox 360 Controller","")==SaturnPadProfile::Standard);
    assert(ChooseSaturnProfile(0x2dc8,0x5006,"8BitDo M30","standard")==SaturnPadProfile::Standard);
    assert(IdentifySaturnPad(0,0,"8BitDo Pro 2")==SaturnPadProfile::Standard);
    const recomp::PadInput custom{SDL_GAMEPAD_BUTTON_RIGHT_STICK,-1};
    assert(ResolveSaturnInput("a",custom,true,SaturnPadProfile::M30)==custom);
    assert(ResolveSaturnInput("a",custom,false,SaturnPadProfile::Standard)==custom);
    assert(ResolveSaturnInput("a",custom,false,SaturnPadProfile::M30).button==SDL_GAMEPAD_BUTTON_SOUTH);
    assert(ResolveSaturnInput("b",custom,false,SaturnPadProfile::M30).button==SDL_GAMEPAD_BUTTON_EAST);
    assert(ResolveSaturnInput("c",custom,false,SaturnPadProfile::M30).axis==SDL_GAMEPAD_AXIS_RIGHT_TRIGGER);
    assert(ResolveSaturnInput("x",custom,false,SaturnPadProfile::M30).button==SDL_GAMEPAD_BUTTON_WEST);
    assert(ResolveSaturnInput("y",custom,false,SaturnPadProfile::M30).button==SDL_GAMEPAD_BUTTON_NORTH);
    assert(ResolveSaturnInput("z",custom,false,SaturnPadProfile::M30).button==SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER);
    assert(ResolveSaturnInput("l",custom,false,SaturnPadProfile::M30).button==SDL_GAMEPAD_BUTTON_LEFT_SHOULDER);
    assert(ResolveSaturnInput("r",custom,false,SaturnPadProfile::M30).axis==SDL_GAMEPAD_AXIS_LEFT_TRIGGER);
    assert(ResolveSaturnInput("up",custom,false,SaturnPadProfile::M30)==custom);
    assert(SDL_Init(SDL_INIT_GAMEPAD));
    SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS,"1");
    SDL_VirtualJoystickDesc desc;SDL_INIT_INTERFACE(&desc);
    desc.type=SDL_JOYSTICK_TYPE_GAMEPAD;desc.vendor_id=0x2dc8;desc.product_id=0x0651;
    desc.name="8BitDo M30 Bluetooth virtual test";desc.naxes=SDL_GAMEPAD_AXIS_COUNT;desc.nbuttons=SDL_GAMEPAD_BUTTON_COUNT;
    desc.button_mask=(1u<<SDL_GAMEPAD_BUTTON_COUNT)-1;desc.axis_mask=(1u<<SDL_GAMEPAD_AXIS_COUNT)-1;
    const auto id=SDL_AttachVirtualJoystick(&desc);assert(id);
    auto* joystick=SDL_OpenJoystick(id);auto* gamepad=SDL_OpenGamepad(id);assert(joystick && gamepad);
    assert(IdentifySaturnPad(SDL_GetGamepadVendor(gamepad),SDL_GetGamepadProduct(gamepad),SDL_GetGamepadName(gamepad))==SaturnPadProfile::M30);
    for(const char* name:{"a","b","c","x","y","z","l","r"}) {
        auto input=ResolveSaturnInput(name,{},false,SaturnPadProfile::M30);
        if(input.button>=0)assert(SDL_SetJoystickVirtualButton(joystick,input.button,true));
        else assert(SDL_SetJoystickVirtualAxis(joystick,input.axis,32767));
        SDL_UpdateJoysticks();
        assert(input.button>=0?SDL_GetGamepadButton(gamepad,SDL_GamepadButton(input.button)):
            SDL_GetGamepadAxis(gamepad,SDL_GamepadAxis(input.axis))>16000);
        if(input.button>=0)SDL_SetJoystickVirtualButton(joystick,input.button,false);
        else SDL_SetJoystickVirtualAxis(joystick,input.axis,-32768);
        SDL_UpdateJoysticks();
    }
    SDL_CloseGamepad(gamepad);SDL_CloseJoystick(joystick);SDL_DetachVirtualJoystick(id);SDL_Quit();

}


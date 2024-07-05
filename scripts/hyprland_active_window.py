from hyprland_dispatcher import HyprlandDispather


def update(dispatcher: HyprlandDispather) -> str:
    window = dispatcher.query("activewindow")
    dispatcher.send(window)
    return window["address"] if "address" in window else None


with HyprlandDispather() as dispatcher:
    address = update(dispatcher)

    for command, arg in dispatcher:
        if "activewindowv2" == command:
            address = update(dispatcher)
        elif "windowtitle" == command and arg == address:
            update(dispatcher)

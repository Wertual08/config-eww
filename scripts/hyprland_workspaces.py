from hyprland_dispatcher import HyprlandDispather


def query_workspaces(dispatcher: HyprlandDispather):
    workspaces = [{
        "id": workspace["id"],
        "name": workspace["name"],
        "monitor_id": workspace["monitorID"],
        "last_window_title": workspace["lastwindowtitle"],
    } for workspace in dispatcher.query("workspaces") if workspace["id"] > 0]

    workspaces.sort(key=lambda item: item["id"])

    return workspaces


def query_active_workspace_name(dispatcher: HyprlandDispather):
    return dispatcher.query("activeworkspace")["name"]


def send(dispatcher: HyprlandDispather, workspaces, active_workspace_name):
    for workspace in workspaces:
        workspace["active"] = workspace["name"] == active_workspace_name

    dispatcher.send(workspaces)


with HyprlandDispather() as dispatcher:
    workspaces = query_workspaces(dispatcher)
    active_workspace_name = query_active_workspace_name(dispatcher)

    send(dispatcher, workspaces, active_workspace_name)

    for command, arg in dispatcher:
        if "workspace" == command:
            active_workspace_name = arg
            send(dispatcher, workspaces, active_workspace_name)
        elif "workspace" in command:
            workspaces = query_workspaces(dispatcher)
            send(dispatcher, workspaces, active_workspace_name)

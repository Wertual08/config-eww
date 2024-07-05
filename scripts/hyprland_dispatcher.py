import socket
import os
import sys
import json
import subprocess


class HyprlandDispather(object):
    def __init__(self):
        XDG_RUNTIME_DIR = os.getenv("XDG_RUNTIME_DIR")
        HYPRLAND_INSTANCE_SIGNATURE = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
        path = f"{XDG_RUNTIME_DIR}/hypr/{HYPRLAND_INSTANCE_SIGNATURE}/.socket2.sock"

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(path)
        self.file = self.socket.makefile()

    def __iter__(self):
        return self

    def __next__(self) -> (str, str):
        line = self.file.readline()
        if line == "":
            raise StopIteration

        return line.rstrip().split(">>", 1)

    def __enter__(self):
        return self

    def __exit__(self):
        self.socket.close()

    def query(self, command: str):
        cmd = subprocess.Popen(
            ["hyprctl", "-j", command],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )

        return json.load(cmd.stdout)

    def send(self, message):
        if isinstance(message, str):
            message = message.replace("\n", " ")
        else:
            message = json.dumps(message)

        print(message, flush=True)

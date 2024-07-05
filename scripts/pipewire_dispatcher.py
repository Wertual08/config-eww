import sys
import json
import subprocess
import logger
import io
import dataclasses


@dataclasses.dataclass
class Event:
    id: int


@dataclasses.dataclass
class DefaultAudioSource(Event):
    name: str


@dataclasses.dataclass
class DefaultAudioSink(Event):
    name: str


@dataclasses.dataclass
class DefaultVideoSource(Event):
    name: str


@dataclasses.dataclass
class AudioDevice(Event):
    name: str


@dataclasses.dataclass
class VideoDevice(Event):
    name: str


@dataclasses.dataclass
class AudioSource(Event):
    name: str
    nick: str
    volume: float
    mute: bool


@dataclasses.dataclass
class AudioSourceVirtual(Event):
    name: str
    nick: str
    volume: float
    mute: bool


@dataclasses.dataclass
class AudioSink(Event):
    name: str
    nick: str
    volume: float
    mute: bool


@dataclasses.dataclass
class AudioDuplex(Event):
    name: str
    nick: str
    volume: float
    mute: bool


@dataclasses.dataclass
class VideoSource(Event):
    name: str
    nick: str


class PipewireDispatcher(object):
    def __init__(self):
        self.process = subprocess.Popen(
            ["pw-dump", "-N", "-m", "e"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )

        self.reader = io.TextIOWrapper(self.process.stdout, encoding="utf-8")

    def __iter__(self):
        return self

    def __next__(self) -> list[Event]:
        lines = []
        for line in self.reader:
            lines.append(line.strip())

            if line.startswith("]"):
                break

        if len(lines) == 0:
            raise StopIteration

        return [
            event
            for item in json.loads("".join(lines))
            if item is not None
            for event in parse_event(item)
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.process.__exit__(exc_type, value, traceback)

    def send(self, message):
        if isinstance(message, str):
            message = message.replace("\n", " ")
        else:
            message = json.dumps(message, cls=EnhancedJSONEncoder)

        print(message, flush=True)


def parse_event(event: dict) -> list[Event]:
    id = event.get("id")
    if id is None:
        return []

    match event.get("type"):
        case "PipeWire:Interface:Metadata":
            return parse_metadata(id, event)
        case "PipeWire:Interface:Device":
            return parse_device(id, event)
        case "PipeWire:Interface:Node":
            return parse_node(id, event)
        case _:
            return []


def parse_metadata(id: int, node: dict) -> list[Event]:
    props = node.get("props")
    if props is None:
        return []

    if props.get("metadata.name") != "default":
        return []

    result = []

    for entry in node["metadata"]:
        match entry["key"]:
            case "default.video.source":
                result.append(DefaultVideoSource(id, entry["value"]["name"]))
            case "default.audio.sink":
                result.append(DefaultAudioSink(id, entry["value"]["name"]))
            case "default.audio.source":
                result.append(DefaultAudioSource(id, entry["value"]["name"]))

    return result


def parse_device(id: int, node: dict) -> list[Event]:
    info = node.get("info")
    if info is None:
        return []

    props = info.get("props")
    if props is None:
        return []

    name = props.get("device.name")
    if name is None:
        return []

    match props.get("media.class"):
        case "Audio/Device":
            return [AudioDevice(id, name)]
        case "Video/Device":
            return [VideoDevice(id, name)]
        case _:
            return []


def parse_node(id: int, node: dict) -> list[Event]:
    info = node.get("info")
    if info is None:
        return []

    props = info.get("props")
    if props is None:
        return []

    name = props.get("node.name")
    if name is None:
        return []

    nick = props.get("node.nick")
    if nick is None:
        nick = props.get("node.description")

    if props.get("media.class") == "Video/Source":
        return [VideoSource(id, name, nick)]

    params = info.get("params")
    if params is None:
        return []

    paramProps = params.get("Props")
    if paramProps is None:
        return []

    paramProps = list(filter(lambda x: "volume" in x, paramProps))

    if len(paramProps) != 1:
        logger.warn(paramProps)

    if len(paramProps) == 0:
        return []

    paramProps = paramProps[0]

    volume = paramProps.get("volume")
    if volume is None:
        return []

    mute = paramProps.get("mute")
    if mute is None:
        return []

    match props.get("media.class"):
        case "Audio/Sink":
            return [AudioSink(id, name, nick, volume, mute)]
        case "Audio/Source":
            return [AudioSource(id, name, nick, volume, mute)]
        case "Audio/Duplex":
            return [AudioDuplex(id, name, nick, volume, mute)]
        case "Audio/Source/Virtual":
            return [AudioSourceVirtual(id, name, nick, volume, mute)]
        case _:
            return []


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

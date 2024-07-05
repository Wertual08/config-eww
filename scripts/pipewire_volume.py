from pipewire_dispatcher import (
    PipewireDispatcher,
    DefaultAudioSource,
    DefaultAudioSink,
    DefaultVideoSource,
    AudioSource,
    AudioSink,
    VideoSource,
)
from logger import warn


default_audio_source = None
default_audio_sink = None
default_video_source = None

audio_sources = {}
audio_sinks = {}
video_sources = {}


def display(dispatcher: PipewireDispatcher):
    update = {
        "default_audio_source": next(
            filter(
                lambda x: x.name == default_audio_source,
                audio_sources.values(),
            ),
            None,
        ),

        "default_audio_sink": next(
            filter(
                lambda x: x.name == default_audio_sink,
                audio_sinks.values(),
            ),
            None,
        ),

        "default_video_source": next(
            filter(
                lambda x: x.name == default_video_source,
                video_sources.values(),
            ),
            None,
        ),
    }

    dispatcher.send(update)


with PipewireDispatcher() as dispatcher:
    for events in dispatcher:
        for event in events:
            match event:
                case DefaultAudioSource():
                    default_audio_source = event.name
                case DefaultAudioSink():
                    default_audio_sink = event.name
                case DefaultVideoSource():
                    default_video_source = event.name
                case AudioSource():
                    audio_sources[event.id] = event
                case AudioSink():
                    audio_sinks[event.id] = event
                case VideoSource():
                    video_sources[event.id] = event
                case _:
                    continue

            display(dispatcher)

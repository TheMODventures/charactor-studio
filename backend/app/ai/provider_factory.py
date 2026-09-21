from app.ai.chatterbox_provider import ChatterboxProvider
from app.ai.kokoro_provider import KokoroProvider
from app.ai.infinitetalk_provider import InfiniteTalkProvider
from app.ai.sadtalker_provider import SadTalkerProvider


def speech_provider(name):
    if name == "kokoro":
        return KokoroProvider()
    if name == "chatterbox":
        return ChatterboxProvider()
    raise ValueError(f"Unsupported speech provider: {name}")


def video_provider(name):
    if name == "sadtalker":
        return SadTalkerProvider()
    if name == "infinitetalk":
        return InfiniteTalkProvider()
    raise ValueError(f"Unsupported video provider: {name}")

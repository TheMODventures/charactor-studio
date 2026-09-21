from pathlib import Path
import subprocess
import wave
from array import array
import sys
import imageio_ffmpeg

RATE = 24000


def wav_read(path):
    with wave.open(str(path), "rb") as wav:
        if (
            wav.getnchannels() != 1
            or wav.getsampwidth() != 2
            or wav.getframerate() != RATE
        ):
            raise ValueError("Expected mono 24 kHz PCM WAV")
        samples = array("h", wav.readframes(wav.getnframes()))
        if sys.byteorder != "little":
            samples.byteswap()
        return samples


def wav_write(path, samples):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        data = array("h", samples)
        if sys.byteorder != "little":
            data.byteswap()
        wav.writeframes(data.tobytes())


class AudioService:
    def normalize(self, source: Path, target: Path, pace=1.0):
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-i",
                str(source),
                "-af",
                f"atempo={pace}",
                "-ac",
                "1",
                "-ar",
                str(RATE),
                "-c:a",
                "pcm_s16le",
                str(target),
            ],
            check=True,
            capture_output=True,
            timeout=90,
        )
        return target

    def align(self, turns, clips, character_ids, folder, target_seconds):
        tracks = {i: array("h") for i in character_ids}
        timeline = []
        cursor = 0
        for turn, clip in zip(turns, clips, strict=True):
            samples = wav_read(clip)
            length = len(samples)
            timeline.append(
                {**turn, "start": cursor / RATE, "end": (cursor + length) / RATE}
            )
            gap = int(turn["pause_after"] * RATE)
            for identity in character_ids:
                tracks[identity].extend(
                    samples
                    if identity == turn["character_id"]
                    else array("h", [0]) * length
                )
                tracks[identity].extend(array("h", [0]) * gap)
            cursor += length + gap
        actual = cursor / RATE
        if abs(actual - target_seconds) > 5:
            raise ValueError(
                f"Speech is {actual:.1f}s; target is {target_seconds}s ±5s. Edit dialogue or pace and render again. Words were not changed."
            )
        length = max(cursor, target_seconds * RATE)
        paths = []
        for index, identity in enumerate(character_ids):
            tracks[identity].extend(array("h", [0]) * (length - cursor))
            path = folder / f"person{index + 1}.wav"
            wav_write(path, tracks[identity])
            paths.append(path)
        mixed = array(
            "h",
            (
                max(-32768, min(32767, a + b))
                for a, b in zip(*tracks.values(), strict=True)
            ),
        )
        wav_write(folder / "mix.wav", mixed)
        return paths, timeline, length / RATE

from pathlib import Path
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw


class VideoService:
    def storyboard(self, image: Path, output: Path, duration: int):
        canvas = Image.open(image).convert("RGB")
        canvas.thumbnail((1280, 650))
        frame = Image.new("RGB", (1280, 720), "#16171c")
        frame.paste(canvas, ((1280 - canvas.width) // 2, (650 - canvas.height) // 2))
        ImageDraw.Draw(frame).text(
            (28, 679),
            "AI CHARACTER STUDIO | STORYBOARD ONLY - NO VOICE OR ANIMATION",
            fill="white",
            font_size=21,
        )
        poster = output.with_suffix(".jpg")
        frame.save(poster)
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-loop",
                "1",
                "-i",
                str(poster),
                "-t",
                str(duration),
                "-r",
                "12",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
            capture_output=True,
            timeout=180,
        )

    def finalize(self, video: Path, audio: Path, output: Path):
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-i",
                str(video),
                "-i",
                str(audio),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-movflags",
                "+faststart",
                "-metadata",
                "comment=AI-generated fictional characters",
                str(output),
            ],
            check=True,
            capture_output=True,
            timeout=300,
        )

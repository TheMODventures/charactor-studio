from app.ai.video_http_provider import VideoHttpProvider


class SadTalkerProvider(VideoHttpProvider):
    """Same multipart transport: fixed scene, two aligned WAVs, output MP4.

    The service splits the scene, animates each portrait and composes the result.
    Text performance directions are deliberately not interpreted by SadTalker.
    """

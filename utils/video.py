import math
from pathlib import Path

import cv2


class VideoPipelineError(Exception):
    """Base exception for recoverable video pipeline failures."""


class VideoOpenError(VideoPipelineError):
    """Raised when OpenCV cannot open a video file."""


class VideoMetadataError(VideoPipelineError):
    """Raised when a video has missing or unusable metadata."""


class VideoOutputError(VideoPipelineError):
    """Raised when the pipeline cannot create or write output files."""


def ensure_dir(path):
    p = Path(path)
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise VideoOutputError(f"Could not create output directory: {p}") from exc
    return p


def get_video_info(video_path: str):
    if not video_path:
        raise VideoOpenError("Please provide a video path.")
    path = Path(video_path).expanduser()
    if not path.exists():
        raise VideoOpenError(f"Video path does not exist: {path}")
    if not path.is_file():
        raise VideoOpenError(f"Video path is not a file: {path}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise VideoOpenError(f"Cannot open video. The file may be corrupt or use an unsupported codec: {path}")

    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    except (TypeError, ValueError) as exc:
        cap.release()
        raise VideoMetadataError(f"Could not read video metadata: {path}") from exc

    if not math.isfinite(fps) or fps <= 0:
        cap.release()
        raise VideoMetadataError(f"Video has invalid FPS metadata: {path}")
    if frame_count <= 0:
        cap.release()
        raise VideoMetadataError(f"Video has no readable frames: {path}")
    if width <= 0 or height <= 0:
        cap.release()
        raise VideoMetadataError(f"Video has invalid resolution metadata: {path}")

    return cap, fps, frame_count, width, height

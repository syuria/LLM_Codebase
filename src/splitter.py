import math
import os
import tempfile
from pathlib import Path
import cv2
import gradio as gr

from utils.video import get_video_info, ensure_dir


def split_video_into_n_parts(video_path: str, num_parts: int, progress=gr.Progress()):
    if not video_path:
        raise gr.Error("Please provide a video path.")

    if not Path(video_path).exists():
        raise gr.Error(f"Video path does not exist: {video_path}")

    cap, fps, frame_count, width, height = get_video_info(video_path)

    output_root = ensure_dir(Path(tempfile.gettempdir()) / "gradio_video_chunks")
    base_name = Path(video_path).stem
    session_dir = ensure_dir(output_root / f"{base_name}_{os.getpid()}")

    frames_per_part = math.ceil(frame_count / num_parts)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    clip_paths = []
    current_frame = 0
    writer = None

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if current_frame % frames_per_part == 0:
            if writer:
                writer.release()

            clip_path = session_dir / f"{base_name}_part_{len(clip_paths)+1:03d}.mp4"
            writer = cv2.VideoWriter(str(clip_path), fourcc, fps, (width, height))
            clip_paths.append(str(clip_path))

        writer.write(frame)
        current_frame += 1

    cap.release()
    if writer:
        writer.release()

    return clip_paths, f"Split into {len(clip_paths)} clips"

# TODO: Handle videos with unsupported codecs
# TODO: Add option to split by duration instead of number of parts
import math
import shutil
import tempfile
import uuid
from pathlib import Path

import cv2

from utils.video import VideoOutputError, VideoPipelineError, ensure_dir, get_video_info


def _validate_num_parts(num_parts, frame_count: int) -> int:
    try:
        parts_as_float = float(num_parts)
    except (TypeError, ValueError) as exc:
        raise VideoPipelineError("Number of parts must be a whole number.") from exc

    if not parts_as_float.is_integer():
        raise VideoPipelineError("Number of parts must be a whole number.")
    parts = int(parts_as_float)

    if parts <= 0:
        raise VideoPipelineError("Number of parts must be greater than zero.")
    if parts > frame_count:
        raise VideoPipelineError(
            f"Number of parts ({parts}) cannot exceed readable frame count ({frame_count})."
        )
    return parts


def _safe_stem(video_path: str) -> str:
    stem = Path(video_path).stem.strip()
    return stem or "video"


def _update_progress(progress, current_frame: int, frame_count: int):
    if progress is None:
        return
    try:
        progress(current_frame / frame_count, desc="Splitting video")
    except TypeError:
        progress(current_frame / frame_count)


def split_video_into_n_parts(video_path: str, num_parts: int, progress=None):
    cap, fps, frame_count, width, height = get_video_info(video_path)
    parts = _validate_num_parts(num_parts, frame_count)

    output_root = ensure_dir(Path(tempfile.gettempdir()) / "gradio_video_chunks")
    base_name = _safe_stem(video_path)
    session_dir = ensure_dir(output_root / f"{base_name}_{uuid.uuid4().hex[:12]}")

    frames_per_part = math.ceil(frame_count / parts)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    clip_paths = []
    current_frame = 0
    writer = None

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if current_frame % frames_per_part == 0:
                if writer:
                    writer.release()

                clip_path = session_dir / f"{base_name}_part_{len(clip_paths)+1:03d}.mp4"
                writer = cv2.VideoWriter(str(clip_path), fourcc, fps, (width, height))
                if not writer.isOpened():
                    raise VideoOutputError(f"Could not create output video: {clip_path}")
                clip_paths.append(str(clip_path))

            writer.write(frame)
            current_frame += 1
            if current_frame == 1 or current_frame % max(frames_per_part, 1) == 0:
                _update_progress(progress, current_frame, frame_count)
    except Exception:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise
    finally:
        cap.release()
        if writer:
            writer.release()

    if current_frame == 0:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise VideoOutputError("No frames were read from the video.")
    if current_frame != frame_count:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise VideoOutputError(
            f"Only read {current_frame} of {frame_count} frames. The video may be truncated or corrupt."
        )

    missing_or_empty = [path for path in clip_paths if not Path(path).is_file() or Path(path).stat().st_size == 0]
    if missing_or_empty:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise VideoOutputError(f"Failed to write {len(missing_or_empty)} output clip(s).")

    _update_progress(progress, frame_count, frame_count)
    return clip_paths, f"Split into {len(clip_paths)} clips in {session_dir}"

# TODO: Handle videos with unsupported codecs
# TODO: Add option to split by duration instead of number of parts

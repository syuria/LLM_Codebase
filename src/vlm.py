import json
import tempfile
import time
from pathlib import Path

import ollama

from utils.video import VideoOutputError, VideoPipelineError, ensure_dir, get_video_info


DEFAULT_MODEL = "qwen3-vl"
MAX_OLLAMA_ATTEMPTS = 3


class VLMError(VideoPipelineError):
    """Raised when clip analysis cannot be completed."""


def _validate_clip_paths(clip_paths):
    if not clip_paths:
        raise VLMError("No clips are available. Split a video before running analysis.")
    return [str(path) for path in clip_paths]


def extract_info_from_clips(clip_paths, progress=None):
    clip_paths = _validate_clip_paths(clip_paths)
    results = []

    for index, clip in enumerate(clip_paths, start=1):
        cap, fps, frame_count, width, height = get_video_info(clip)
        cap.release()

        results.append({
            "clip": Path(clip).name,
            "frames": frame_count,
            "fps": fps,
            "resolution": f"{width}x{height}"
        })
        if progress is not None:
            try:
                progress(index / len(clip_paths), desc="Reading clip metadata")
            except TypeError:
                progress(index / len(clip_paths))

    return json.dumps(results, indent=2)


def get_selected_clip(selected_name, clip_paths):
    for i, path in enumerate(clip_paths):
        if Path(path).name == selected_name:
            return i, path
    return None, None


def extract_info_from_selected_clip(selected_name, clip_paths):
    _validate_clip_paths(clip_paths)
    idx, path = get_selected_clip(selected_name, clip_paths)

    if path is None:
        raise VLMError("Selected clip was not found. Choose a clip from the list.")

    prompt = "Summarise the video and list objects"

    last_error = None
    for attempt in range(1, MAX_OLLAMA_ATTEMPTS + 1):
        try:
            response = ollama.chat(
                model=DEFAULT_MODEL,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            content = response.get("message", {}).get("content")
            if not content:
                raise VLMError("Ollama returned an empty response.")

            output_dir = ensure_dir(Path(tempfile.gettempdir()) / "gradio_video_analysis")
            output_path = output_dir / f"{Path(path).stem}_analysis.json"
            payload = {
                "clip": Path(path).name,
                "clip_index": idx,
                "model": DEFAULT_MODEL,
                "analysis": content,
            }
            tmp_path = output_path.with_suffix(".tmp")
            try:
                tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                tmp_path.replace(output_path)
            except OSError as exc:
                raise VideoOutputError(f"Could not save analysis output: {output_path}") from exc
            return content, str(output_path)
        except VideoPipelineError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt < MAX_OLLAMA_ATTEMPTS:
                time.sleep(0.5 * attempt)

    raise VLMError(
        f"Ollama analysis failed after {MAX_OLLAMA_ATTEMPTS} attempts. "
        "Check that Ollama is running and the qwen3-vl model is installed."
    ) from last_error

# TODO: Allow user to select model name from UI

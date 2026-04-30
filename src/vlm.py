import json
from pathlib import Path
import ollama

from utils.video import get_video_info


def extract_info_from_clips(clip_paths, progress):
    results = []

    for clip in clip_paths:
        cap, fps, frame_count, width, height = get_video_info(clip)
        cap.release()

        results.append({
            "clip": Path(clip).name,
            "frames": frame_count,
            "fps": fps,
            "resolution": f"{width}x{height}"
        })

    return json.dumps(results, indent=2)


def get_selected_clip(selected_name, clip_paths):
    for i, path in enumerate(clip_paths):
        if Path(path).name == selected_name:
            return i, path
    return None, None


def extract_info_from_selected_clip(selected_name, clip_paths):
    idx, path = get_selected_clip(selected_name, clip_paths)

    if path is None:
        raise ValueError("Clip not found")

    prompt = "Summarise the video and list objects"

    response = ollama.chat(
        model="qwen3-vl",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return response["message"]["content"], "saved.json"

# TODO: Add retry logic if Ollama connection fails
# TODO: Validate model output before saving JSON
# TODO: Allow user to select model name from UI
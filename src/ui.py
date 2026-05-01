import logging
from pathlib import Path

import gradio as gr

from src.splitter import split_video_into_n_parts
from src.vlm import extract_info_from_clips, extract_info_from_selected_clip
from utils.video import VideoPipelineError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _as_gradio_error(exc: Exception):
    if isinstance(exc, VideoPipelineError):
        raise gr.Error(str(exc)) from exc
    logger.exception("Unexpected pipeline failure")
    raise gr.Error("Unexpected pipeline failure. Check the server logs for details.") from exc


with gr.Blocks() as demo:

    video_path = gr.Textbox(label="Video path")
    num_parts = gr.Number(value=4)

    split_btn = gr.Button("Split Video")
    analyze_btn = gr.Button("Analyze All")
    extract_btn = gr.Button("Analyze Selected")

    clip_state = gr.State([])

    dropdown = gr.Dropdown(label="Clips", choices=[])
    video_player = gr.Video()

    output = gr.Code()
    json_path = gr.Textbox()
    status = gr.Markdown()

    def split(video_path, num_parts, progress=gr.Progress()):
        try:
            clips, msg = split_video_into_n_parts(video_path, num_parts, progress=progress)
            names = [Path(p).name for p in clips]
            selected = names[0] if names else None
            return clips, gr.update(choices=names, value=selected), msg
        except Exception as exc:
            _as_gradio_error(exc)

    def preview(name, clips):
        if not name or not clips:
            return None
        for p in clips:
            if Path(p).name == name:
                return p
        raise gr.Error("Selected clip is no longer available.")

    def analyze_all(clips, progress=gr.Progress()):
        try:
            return extract_info_from_clips(clips, progress=progress)
        except Exception as exc:
            _as_gradio_error(exc)

    def analyze_selected(name, clips):
        try:
            return extract_info_from_selected_clip(name, clips)
        except Exception as exc:
            _as_gradio_error(exc)

    split_btn.click(split, [video_path, num_parts], [clip_state, dropdown, status])

    dropdown.change(preview, [dropdown, clip_state], video_player)

    analyze_btn.click(analyze_all, [clip_state], output)

    extract_btn.click(
        analyze_selected,
        [dropdown, clip_state],
        [output, json_path]
    )


if __name__ == "__main__":
    demo.launch()

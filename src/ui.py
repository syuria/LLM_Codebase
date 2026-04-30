import gradio as gr
from pathlib import Path

from src.splitter import split_video_into_n_parts
from src.vlm import extract_info_from_clips, extract_info_from_selected_clip


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

    def split(video_path, num_parts):
        clips, msg = split_video_into_n_parts(video_path, int(num_parts))
        names = [Path(p).name for p in clips]
        return clips, gr.update(choices=names, value=names[0])

    def preview(name, clips):
        for p in clips:
            if Path(p).name == name:
                return p

    split_btn.click(split, [video_path, num_parts], [clip_state, dropdown])

    dropdown.change(preview, [dropdown, clip_state], video_player)

    analyze_btn.click(extract_info_from_clips, [clip_state], output)

    extract_btn.click(
        extract_info_from_selected_clip,
        [dropdown, clip_state],
        [output, json_path]
    )


if __name__ == "__main__":
    demo.launch()
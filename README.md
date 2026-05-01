# Video Splitter + VLM Analyzer

This project provides a Gradio interface for splitting a video into smaller clips and analyzing selected clips with an Ollama-backed vision-language model.

## Features

- Split a video into multiple smaller clips
- Validate input paths, video metadata, split counts, and output writes
- Clean up partial output files when splitting fails
- Preview selected clips in the browser
- Extract metadata from all clips
- Analyze a selected clip using Ollama with retry handling
- Save selected-clip analysis as JSON

## Project Structure

```text
project/
├── src/
│   ├── ui.py          # Gradio user interface and UI-safe error handling
│   ├── splitter.py    # Video splitting logic
│   ├── vlm.py         # VLM / Ollama processing logic
│   └── prompt.txt     # Prompt template for VLM analysis
├── tests/
├── utils/
│   └── video.py       # Shared video utilities and pipeline exceptions
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

```text
gradio
opencv-python
ollama
```

## Running the App

```bash
python3 -m src.ui
```

## Ollama Setup

Make sure Ollama is running and a vision-capable model is available:

```bash
ollama list
```

Default model:

```text
qwen3-vl
```

## Tests

```bash
python3 -m unittest discover -s tests
```

The splitter tests generate a tiny local MP4. They are skipped automatically when `opencv-python` is not installed.

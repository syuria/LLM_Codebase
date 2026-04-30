# Video Splitter + VLM Analyzer

This project provides a Gradio interface for splitting a video into smaller clips and analysing selected clips using a Vision-Language Model through Ollama.

## Features

- Split a video into multiple smaller clips
- Preview selected clips in the browser
- Extract metadata from all clips
- Analyse a selected clip using a VLM
- Save extracted information as JSON

## Project Structure

```text
project/ 
├──src/ 
   ├── ui.py # Gradio user interface 
   ├── splitter.py # Video splitting logic 
   ├── vlm.py # VLM / Ollama processing logic 
   ├── prompt.txt # Prompt template for VLM analysis 
├── tests 
├── utils 
   ├── video.py # Shared video utility functions 
├── requirements.txt 
└── README.md
```

Installation
```bash
pip install -r requirements.txt
````

Requirement
```
gradio
opencv-python
ollama
```

Running the App
```bash
python ui.py
```

Ollama Setup

Make sure Ollama is running and a vision-capable model is available:

```bash
ollama list
```

Example model:
```bash
qwen3-vl
```
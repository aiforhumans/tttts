# Coqui TTS - Advanced Gradio App

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![TTS](https://img.shields.io/badge/TTS-0.22.0-orange)](https://github.com/coqui-ai/TTS)
[![Gradio](https://img.shields.io/badge/Gradio-5.33.0-green)](https://gradio.app/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

---

## Project Overview

Coqui TTS - Advanced Gradio App is a local text-to-speech synthesis application leveraging state-of-the-art Coqui TTS models. It enables users to generate high-quality speech audio directly on their GPU-enabled machine, providing a fast, customizable, and privacy-preserving alternative to cloud-based TTS services.

This app supports multiple voice models, adjustable speech speed, and saves generated audio files with timestamped filenames for easy access and management.

---

## Features

- 🎤 Multiple pre-trained voice models selectable via dropdown
- ⚡ Real-time speech synthesis accelerated by GPU (tested on RTX 5080)
- ⏩ Adjustable speech speed slider (0.5x to 1.5x)
- 💾 Automatic saving of generated audio files in `output/` folder with timestamped filenames
- 🖥️ Intuitive and responsive UI built with Gradio
- 🔄 Dynamic model loading to optimize resource usage

---

## Architecture and Workflow

1. **Model Management**: The app maintains a dictionary of available TTS models. When a user selects a different voice model, the app dynamically loads the corresponding model onto the GPU.
2. **Speech Synthesis**: Upon text input and parameter selection, the app synthesizes speech using the selected model and speed setting, saving the output as a WAV file.
3. **User Interface**: Gradio provides a clean interface with text input, model selector, speed slider, and audio playback components. The "Generate Speech" button triggers synthesis and updates the audio output.
4. **File Management**: Generated audio files are saved in the `output/` directory with filenames including timestamps to avoid overwriting and facilitate organization.

---

## Supported Voice Models

| Model Name               | Description                          |
|--------------------------|------------------------------------|
| LJSpeech - Tacotron2-DDC | Tacotron2 with DDC on LJSpeech dataset (English, female voice) |
| LJSpeech - GlowTTS       | GlowTTS model on LJSpeech dataset (English, female voice)      |
| VCTK - Tacotron2-DDC     | Tacotron2 with DDC on VCTK dataset (English, multi-speaker)     |

---

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- NVIDIA GPU with CUDA support (tested on RTX 5080)
- CUDA Toolkit and drivers installed

### Steps

1. **Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/Scripts/activate  # On Windows CMD use: .venv\Scripts\activate
```

2. **Install GPU-enabled PyTorch**

```bash
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

3. **Install project dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
python app.py
```

---

## Usage Guide

- Enter the text you want to synthesize in the text box.
- Select a voice model from the dropdown menu.
- Adjust the speech speed slider to your preference (0.5x to 1.5x).
- Click the "Generate Speech 🎙️" button.
- Listen to the generated audio in the player.
- All generated audio files are saved in the `output/` folder with timestamped filenames.

---

## Performance and GPU Utilization

- The app leverages GPU acceleration via CUDA for fast and efficient speech synthesis.
- Models are loaded dynamically to minimize GPU memory usage.
- Tested on NVIDIA RTX 5080, but should work on other CUDA-compatible GPUs.
- For CPU-only usage, modifications are needed to remove `.to("cuda")` calls.

---

## Troubleshooting and FAQ

**Q: The app crashes or runs out of GPU memory.**  
A: Try selecting a lighter model or reduce concurrent usage. Ensure your GPU drivers and CUDA toolkit are up to date.

**Q: How to add new voice models?**  
A: Add the model name and path to the `MODELS` dictionary in `app.py`. Ensure the model is compatible with Coqui TTS.

**Q: Can I run this without a GPU?**  
A: The current setup requires a CUDA-enabled GPU. To run on CPU, remove `.to("cuda")` calls and install CPU versions of PyTorch and dependencies.

---

## Contributing

Contributions are welcome! Please open issues or pull requests for bug fixes, features, or improvements.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Coqui TTS](https://github.com/coqui-ai/TTS) for the powerful text-to-speech models  
- [Gradio](https://gradio.app/) for the easy-to-use UI framework

---

Enjoy advanced local TTS! 🎙️🚀

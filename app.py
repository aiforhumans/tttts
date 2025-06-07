import gradio as gr
from TTS.api import TTS
import edge_tts
import asyncio
import tempfile
import os
import time
import json
import traceback
import zipfile

# Fetch list of available Edge TTS voices
def fetch_edge_voices():
    """Return list of Edge TTS voice short names."""
    try:
        voices = asyncio.run(edge_tts.list_voices())
        return [voice["ShortName"] for voice in voices]
    except Exception as e:
        # Log the error but fall back to a single default voice
        log_error_to_json(f"Failed to fetch Edge voices: {str(e)}")
        return ["en-US-GuyNeural"]

# Available models (backend, model identifier)
MODELS = {
    "LJSpeech - Tacotron2-DDC": ("coqui", "tts_models/en/ljspeech/tacotron2-DDC"),
    "LJSpeech - GlowTTS": ("coqui", "tts_models/en/ljspeech/glow-tts"),
    "VCTK - VITS": ("coqui", "tts_models/en/vctk/vits"),
    "LJSpeech - FastPitch": ("coqui", "tts_models/en/ljspeech/fast_pitch"),
    "EdgeTTS - en-US-GuyNeural": ("edge", "en-US-GuyNeural"),
}

# Lazy initialization and caching
model_cache = {}
model_speakers = {}
cache_order = []
CACHE_LIMIT = 2
current_model_name = None
current_speaker = None
tts = None

# Output folder
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def preprocess_text(text: str) -> str:
    """Simple text normalization before synthesis."""
    text = text.lower()
    text = " ".join(text.split())
    return text

def get_tts(model_identifier: str):
    """Return cached TTS instance or load a new one lazily."""
    global model_cache, cache_order
    if model_identifier in model_cache:
        return model_cache[model_identifier]
    # enforce cache limit
    if len(model_cache) >= CACHE_LIMIT:
        oldest = cache_order.pop(0)
        model_cache.pop(oldest, None)
    try:
        tts_obj = TTS(model_name=model_identifier, progress_bar=False)
        tts_obj.to("cuda")
        model_cache[model_identifier] = tts_obj
        cache_order.append(model_identifier)
        model_speakers[model_identifier] = getattr(tts_obj, "speakers", [])
        return tts_obj
    except Exception as e:
        log_error_to_json(f"Error loading model {model_identifier}: {str(e)}\n{traceback.format_exc()}")
        raise

def preview_model(model_name):
    """Return the path to a sample audio for the selected model if available."""
    sample = SAMPLES.get(model_name)
    return sample if sample and os.path.exists(sample) else None

def log_error_to_json(error_message):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "error": error_message
    }
    log_file = os.path.join(OUTPUT_FOLDER, "error_log.json")
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
    except Exception:
        logs = []
    logs.append(log_entry)
    # Rotate log if too large (keep last 500 entries)
    if len(logs) > 500:
        logs = logs[-500:]
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

# Extend MODELS with all available Edge voices
EDGE_VOICES = fetch_edge_voices()
for voice in EDGE_VOICES:
    MODELS[f"EdgeTTS - {voice}"] = ("edge", voice)

# Local samples for model preview
SAMPLES = {name: os.path.join("samples", name.replace(" ", "_") + ".wav") for name in MODELS}

def synthesize_speech(text, model_name, speed, speaker):
    global tts, current_model_name, current_speaker
    backend, identifier = MODELS[model_name]
    text = preprocess_text(text)
    try:
        if backend == "coqui":
            tts = get_tts(identifier)
            current_model_name = identifier
            speakers = model_speakers.get(identifier, [])
            if speakers:
                current_speaker = speakers[0]
        else:
            current_model_name = identifier
            tts = None
    except Exception:
        gr.Error(f"Failed to load model {model_name}")
        return None



    # Generate filename
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(OUTPUT_FOLDER, f"tts_output_{timestamp}.wav")

    # Synthesize speech
    try:
        if backend == "coqui":
            if current_speaker:
                tts.tts_to_file(text=text, file_path=filename, speed=speed, speaker=speaker)
            else:
                tts.tts_to_file(text=text, file_path=filename, speed=speed)
        else:
            rate = f"{speed*100 - 100:+.0f}%"
            communicate = edge_tts.Communicate(text=text, voice=identifier, rate=rate)
            asyncio.run(communicate.save(filename))
    except Exception as e:
        error_message = f"Error during synthesis: {str(e)}\\n{traceback.format_exc()}"
        log_error_to_json(error_message)
        return None

    return filename

def batch_synthesize(text_lines, text_file, model_name, speed, speaker):
    lines = []
    if text_lines:
        lines.extend([line.strip() for line in text_lines.splitlines() if line.strip()])
    if text_file is not None:
        try:
            content = text_file.decode("utf-8")
        except AttributeError:
            text_file.seek(0)
            content = text_file.read().decode("utf-8")
        lines.extend([line.strip() for line in content.splitlines() if line.strip()])
    if not lines:
        return None
    generated = []
    for line in lines:
        fn = synthesize_speech(line, model_name, speed, speaker)
        if fn:
            generated.append(fn)
    if not generated:
        return None
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(tmp.name, "w") as zf:
        for f in generated:
            zf.write(f, os.path.basename(f))
    return tmp.name

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🎤 Coqui TTS - Advanced")
    gr.Markdown("Generate speech locally using your GPU (RTX 5080).")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Enter text", lines=5, placeholder="Type something here...")
            model_selector = gr.Dropdown(label="Select Voice Model", choices=list(MODELS.keys()), value=list(MODELS.keys())[0])
            speed_slider = gr.Slider(label="Speech Speed", minimum=0.5, maximum=1.5, value=1.0, step=0.05)
            speaker_selector = gr.Dropdown(label="Select Speaker", choices=[], value=None, visible=False)
            generate_button = gr.Button("Generate Speech 🎙️")
            preview_button = gr.Button("Preview Voice 🎧")
            batch_text = gr.Textbox(label="Batch Text (one line per item)", lines=5)
            batch_file = gr.File(label="Or upload text file", file_types=[".txt"])
            batch_button = gr.Button("Batch Generate 📦")
        with gr.Column():
            audio_output = gr.Audio(label="Generated Speech", interactive=False)
            batch_output = gr.File(label="Batch Output")
            gr.Markdown("👉 All generated files saved in `/output` folder.")

    def update_speakers(model_name):
        backend, identifier = MODELS[model_name]
        if backend == "edge":
            return gr.update(choices=[], value=None, visible=False)
        speakers_temp = model_speakers.get(identifier)
        if speakers_temp is None:
            try:
                tts_temp = get_tts(identifier)
                speakers_temp = model_speakers.get(identifier, [])
            except Exception as e:
                error_message = f"Error updating speakers for model {model_name}: {str(e)}\\n{traceback.format_exc()}"
                log_error_to_json(error_message)
                return gr.update(choices=[], value=None, visible=False)
        return gr.update(choices=speakers_temp, value=speakers_temp[0] if speakers_temp else None, visible=bool(speakers_temp))

    model_selector.change(fn=update_speakers, inputs=[model_selector], outputs=[speaker_selector])

    generate_button.click(
        fn=synthesize_speech,
        inputs=[text_input, model_selector, speed_slider, speaker_selector],
        outputs=[audio_output]
    )

    preview_button.click(
        fn=preview_model,
        inputs=[model_selector],
        outputs=[audio_output]
    )

    batch_button.click(
        fn=batch_synthesize,
        inputs=[batch_text, batch_file, model_selector, speed_slider, speaker_selector],
        outputs=[batch_output]
    )

# Launch
if __name__ == "__main__":
    demo.queue().launch()

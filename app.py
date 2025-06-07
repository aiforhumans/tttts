import gradio as gr
from TTS.api import TTS
import tempfile
import os
import time
import json
import traceback

# Available models
MODELS = {
    "LJSpeech - Tacotron2-DDC": "tts_models/en/ljspeech/tacotron2-DDC",
    "LJSpeech - GlowTTS": "tts_models/en/ljspeech/glow-tts",
    "VCTK - VITS": "tts_models/en/vctk/vits",
    "LJSpeech - FastPitch": "tts_models/en/ljspeech/fast_pitch",
}

# Initialize TTS with default model
current_model_name = list(MODELS.values())[0]
tts = TTS(model_name=current_model_name, progress_bar=False)
tts.to("cuda")

# Get speakers if multi-speaker model
speakers = getattr(tts, "speakers", [])
current_speaker = speakers[0] if speakers else None

# Output folder
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

def synthesize_speech(text, model_name, speed, speaker):
    global tts, current_model_name, current_speaker

    # Load new model if changed
    selected_model = MODELS[model_name]
    if selected_model != current_model_name:
        try:
            tts = TTS(model_name=selected_model, progress_bar=False)
            tts.to("cuda")
            current_model_name = selected_model
            speakers = getattr(tts, "speakers", [])
            current_speaker = speakers[0] if speakers else None
        except Exception as e:
            error_message = f"Error loading model {selected_model}: {str(e)}\\n{traceback.format_exc()}"
            log_error_to_json(error_message)
            return None

    # Generate filename
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(OUTPUT_FOLDER, f"tts_output_{timestamp}.wav")

    # Synthesize speech
    try:
        if current_speaker:
            tts.tts_to_file(text=text, file_path=filename, speed=speed, speaker=speaker)
        else:
            tts.tts_to_file(text=text, file_path=filename, speed=speed)
    except Exception as e:
        error_message = f"Error during synthesis: {str(e)}\\n{traceback.format_exc()}"
        log_error_to_json(error_message)
        return None

    return filename

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🎤 Coqui TTS - Advanced")
    gr.Markdown("Generate speech locally using your GPU (RTX 5080).")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Enter text", lines=5, placeholder="Type something here...")
            model_selector = gr.Dropdown(label="Select Voice Model", choices=list(MODELS.keys()), value=list(MODELS.keys())[0])
            speed_slider = gr.Slider(label="Speech Speed", minimum=0.5, maximum=1.5, value=1.0, step=0.05)
            speaker_selector = gr.Dropdown(label="Select Speaker", choices=speakers, value=current_speaker if current_speaker else None, visible=bool(speakers))
            generate_button = gr.Button("Generate Speech 🎙️")
        with gr.Column():
            audio_output = gr.Audio(label="Generated Speech", interactive=False)
            gr.Markdown("👉 All generated files saved in `/output` folder.")

    def update_speakers(model_name):
        try:
            selected_model = MODELS[model_name]
            tts_temp = TTS(model_name=selected_model, progress_bar=False)
            speakers_temp = getattr(tts_temp, "speakers", [])
            return gr.update(choices=speakers_temp, value=speakers_temp[0] if speakers_temp else None, visible=bool(speakers_temp))
        except Exception as e:
            error_message = f"Error updating speakers for model {model_name}: {str(e)}\\n{traceback.format_exc()}"
            log_error_to_json(error_message)
            return gr.update(choices=[], value=None, visible=False)

    model_selector.change(fn=update_speakers, inputs=[model_selector], outputs=[speaker_selector])

    generate_button.click(
        fn=synthesize_speech,
        inputs=[text_input, model_selector, speed_slider, speaker_selector],
        outputs=[audio_output]
    )

# Launch
if __name__ == "__main__":
    demo.launch()

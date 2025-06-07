from TTS.api import TTS

def download_model():
    model_name = "tts_models/en/ljspeech/fast_pitch"
    tts = TTS(model_name=model_name)
    print(f"Model {model_name} downloaded successfully.")

if __name__ == "__main__":
    download_model()

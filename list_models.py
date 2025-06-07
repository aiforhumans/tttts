from TTS.api import TTS

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
model_manager = tts.list_models()
print(model_manager.models_dict)

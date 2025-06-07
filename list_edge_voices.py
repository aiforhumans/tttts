import asyncio
import edge_tts

async def main():
    try:
        voices = await edge_tts.list_voices()
    except Exception as e:
        print(f"Failed to fetch voices: {e}")
        return
    for voice in voices:
        name = voice.get("ShortName")
        gender = voice.get("Gender")
        categories = ",".join(voice["VoiceTag"]["ContentCategories"])
        personalities = ",".join(voice["VoiceTag"]["VoicePersonalities"])
        print(f"{name}\t{gender}\t{categories}\t{personalities}")

if __name__ == "__main__":
    asyncio.run(main())

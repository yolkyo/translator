import whisper
import sounddevice as sd
import numpy as np
import asyncio
import websockets
from googletrans import Translator

model = whisper.load_model("small")
translator = Translator()
duration = 5
sample_rate = 16000

async def send_translation(websocket, path):
    while True:
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        audio_data = np.squeeze(audio)
        result = model.transcribe(audio_data, fp16=False)
        original_text = result["text"]
        translated = translator.translate(original_text, src="auto", dest="zh-TW")
        await websocket.send(translated.text)

start_server = websockets.serve(send_translation, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

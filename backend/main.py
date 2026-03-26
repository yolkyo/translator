import whisper
import sounddevice as sd
import numpy as np
import asyncio
import websockets
from googletrans import Translator

model = whisper.load_model("small")
translator = Translator()
duration = 1
sample_rate = 16000

# 找出可用裝置
print(sd.query_devices())

# 設定 Virtual Cable 為輸入裝置 (通常是 "CABLE Output")
sd.default.device = "CABLE Output (VB-Audio Virtual Cable)"

async def send_translation(websocket, path):
    while True:
        print("🎧 錄製直播音訊中...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        audio_data = np.squeeze(audio)
        result = model.transcribe(audio_data, fp16=False)
        original_text = result["text"]
        translated = translator.translate(original_text, src="auto", dest="zh-TW")
        await websocket.send(translated.text)

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        await asyncio.Future()
asyncio.run(main())

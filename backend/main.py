import whisper
import sounddevice as sd
import asyncio
import websockets
from googletrans import Translator
import numpy as np
import soundfile as sf

device_id = 40   # CABLE Output (VB-Audio Virtual Cable), Windows WASAPI
channels = 2
sample_rate = 48000

model = whisper.load_model("small")
translator = Translator()

async def send_translation(websocket):
    audio_buffer = []

    def callback(indata, frames, time, status):
        audio_buffer.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate,
                        channels=channels,
                        device=device_id,
                        dtype='float32',
                        callback=callback):
        while True:
            await asyncio.sleep(1)  # 每秒處理一次
            if audio_buffer:
                audio = np.concatenate(audio_buffer, axis=0)
                audio_buffer.clear()

                sf.write("temp.wav", audio, sample_rate)

                result = model.transcribe("temp.wav", fp16=False)
                original_text = result["text"].strip()

                if original_text:  # 只送出有內容的翻譯
                    translated = translator.translate(original_text, src="auto", dest="zh-TW")
                    # 用 "||" 分隔原文與翻譯
                    await websocket.send(f"{original_text}||{translated.text}")

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        print("✅ WebSocket 伺服器已啟動，等待前端連線...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

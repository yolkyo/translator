import whisper
import sounddevice as sd
import asyncio
import websockets
from googletrans import Translator
import numpy as np

device_id = 40   # CABLE Output (VB-Audio Virtual Cable), Windows WASAPI
channels = 2
sample_rate = 48000

model = whisper.load_model("small")
translator = Translator()

async def send_translation(websocket):
    loop = asyncio.get_event_loop()
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

                # Whisper 辨識
                sf_path = "temp.wav"
                import soundfile as sf
                sf.write(sf_path, audio, sample_rate)

                result = model.transcribe(sf_path, fp16=False)
                original_text = result["text"].strip()

                if original_text:
                    translated = translator.translate(original_text, src="auto", dest="zh-TW")
                    await websocket.send(translated.text)

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        print("✅ WebSocket 伺服器已啟動，等待前端連線...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

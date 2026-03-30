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

                # 取 Whisper 的 no_speech_prob（判斷是否為靜音）
                segments = result.get("segments", [])
                no_speech_prob = segments[0]["no_speech_prob"] if segments else 1.0

                # 過濾條件：
                # 1. 必須有文字
                # 2. 如果字數大於 2，直接送出
                # 3. 如果字數 ≤ 2，但模型判斷不是靜音 (no_speech_prob < 0.3)，也允許送出
                # 4. 可選：排除常見假字幕（例如 "謝謝", "Thank you"）
                blacklist = ["謝謝", "Thank you"]

                if original_text and (len(original_text) > 2 or no_speech_prob < 0.3):
                    if original_text not in blacklist:
                        translated = translator.translate(original_text, src="auto", dest="zh-TW")
                        try:
                            await websocket.send(f"{original_text}|{translated.text}")
                        except websockets.exceptions.ConnectionClosedOK:
                            print("🔴 前端已斷線，停止錄音")

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        print("✅ WebSocket 伺服器已啟動，等待前端連線...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

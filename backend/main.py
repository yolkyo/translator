import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import asyncio
import websockets
from googletrans import Translator

# 明確指定 WASAPI 的 Virtual Cable
device_id = 40   # 請確認這是 WASAPI 的 index
channels = 2
sample_rate = 48000

# 檢查裝置設定
sd.check_input_settings(device=device_id, samplerate=sample_rate, channels=channels)

# 載入 Whisper 模型
model = whisper.load_model("small")
translator = Translator()

duration = 5  # 每次錄音秒數

def record_once():
    """使用 InputStream 錄音，避免 sd.rec() 的名字解析問題"""
    with sd.InputStream(samplerate=sample_rate,
                        channels=channels,
                        device=device_id,
                        dtype='float32') as stream:
        audio, _ = stream.read(int(duration * sample_rate))
        return np.array(audio)

async def send_translation(websocket): 
    while True:
        try:
            print("🎧 錄製直播音訊中...")
            audio = record_once()

            # 存成暫存檔
            sf.write("temp.wav", audio, sample_rate)

            # Whisper 辨識
            result = model.transcribe("temp.wav", fp16=False)
            original_text = result["text"].strip()

            if original_text:
                print("📝 辨識結果:", original_text)
                translated = translator.translate(original_text, src="auto", dest="zh-TW")
                print("🌐 翻譯結果:", translated.text)
                await websocket.send(translated.text)
            else:
                await websocket.send("⚠️ 沒有辨識到有效語音")

        except Exception as e:
            error_msg = f"⚠️ 錄音或翻譯錯誤: {e}"
            print(error_msg)
            try:
                await websocket.send(error_msg)
            except:
                print("⚠️ WebSocket 尚未建立，無法傳送錯誤訊息")

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        print("✅ WebSocket 伺服器已啟動，等待前端連線...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

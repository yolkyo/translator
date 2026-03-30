import whisper
import sounddevice as sd
import numpy as np
import asyncio
import websockets
from googletrans import Translator

# 載入 Whisper 模型
model = whisper.load_model("small")
translator = Translator()

# 音訊設定
duration = 5        # 每次錄音秒數
sample_rate = 16000 # 取樣率

# 指定音訊裝置 (先用 sd.query_devices() 找出正確名稱或編號)
sd.default.device = (6, None)  # 使用 CABLE Input (VB-Audio Virtual Cable)

async def send_translation(websocket): 
    while True:
        print("🎧 錄製直播音訊中...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        audio_data = np.squeeze(audio)

        # Whisper 辨識
        result = model.transcribe(audio_data, fp16=False)
        original_text = result["text"].strip()

        if original_text:
            print("📝 辨識結果:", original_text)
            # 翻譯成中文
            translated = translator.translate(original_text, src="auto", dest="zh-TW")
            print("🌐 翻譯結果:", translated.text)
            await websocket.send(translated.text)

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        print("✅ WebSocket 伺服器已啟動，等待前端連線...")
        await asyncio.Future()  # 保持伺服器運行

if __name__ == "__main__":
    asyncio.run(main())

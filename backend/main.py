import whisper
import sounddevice as sd
import soundfile as sf
import asyncio
import websockets
from googletrans import Translator

# 載入 Whisper 模型
model = whisper.load_model("small")
translator = Translator()

# 音訊設定
duration = 5         # 每次錄音秒數
sample_rate = 48000  # Virtual Cable 常用支援的取樣率
device_id = 47       # WASAPI 的 CABLE Output
channels = 2

try:
    sd.check_input_settings(device=device_id, samplerate=sample_rate, channels=channels)
except Exception as e:
    print(f"⚠️ 錯誤：裝置設定不支援 → {e}")
    return
    
async def send_translation(websocket): 
    while True:
        try:
            print("🎧 錄製直播音訊中...")
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                dtype='float32',
                device=device_id
            )
            except Exception as e:
            error_msg = f"⚠️ 系統錯誤: {e}"
            print(error_msg)
            try:
                await websocket.send(error_msg)
            except:
                print("⚠️ WebSocket 尚未建立，無法傳送錯誤訊息")
            sd.wait()

            # 存成暫存檔，Whisper 讀檔最穩定
            sf.write("temp.wav", audio, sample_rate)

            # Whisper 辨識
            try:
                result = model.transcribe("temp.wav", fp16=False)
                original_text = result["text"].strip()
            except Exception as e:
                error_msg = f"⚠️ Whisper 辨識錯誤: {e}"
                print(error_msg)
                await websocket.send(error_msg)
                continue

            if original_text:
                print("📝 辨識結果:", original_text)
                # 翻譯成中文
                try:
                    translated = translator.translate(original_text, src="auto", dest="zh-TW")
                    print("🌐 翻譯結果:", translated.text)
                    await websocket.send(translated.text)
                except Exception as e:
                    error_msg = f"⚠️ 翻譯錯誤: {e}"
                    print(error_msg)
                    await websocket.send(error_msg)
            else:
                await websocket.send("⚠️ 沒有辨識到有效語音")

        except Exception as e:
            error_msg = f"⚠️ 錄音錯誤: {e}"
            print(error_msg)
            await websocket.send(error_msg)

async def main():
    async with websockets.serve(send_translation, "localhost", 8765):
        print("✅ WebSocket 伺服器已啟動，等待前端連線...")
        await asyncio.Future()  # 保持伺服器運行

if __name__ == "__main__":
    asyncio.run(main())

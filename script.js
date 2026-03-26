// 建立 WebSocket 連線
const ws = new WebSocket("ws://localhost:8765");

// 連線成功
ws.onopen = () => {
  console.log("✅ 已連線到後端 WebSocket");
};

// 收到訊息時更新字幕
ws.onmessage = (event) => {
  const subtitleDiv = document.getElementById("subtitle");
  subtitleDiv.textContent = event.data;
  console.log("🌐 收到翻譯:", event.data);
};

// 連線錯誤
ws.onerror = (error) => {
  console.error("❌ WebSocket 錯誤:", error);
};

// 連線關閉
ws.onclose = () => {
  console.log("🔌 WebSocket 已關閉");
};

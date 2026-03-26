const subtitle = document.getElementById("subtitle");
const ws = new WebSocket("ws://localhost:8765");

ws.onmessage = (event) => {
  subtitle.style.opacity = 0;
  setTimeout(() => {
    subtitle.textContent = event.data;
    subtitle.style.opacity = 1;
  }, 300);
};

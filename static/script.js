document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatBox");
  const messageInput = document.getElementById("messageInput");
  const sendMessageBtn = document.getElementById("sendMessage");
  const audioPlayer = document.getElementById("audioPlayer");
  const timer = document.getElementById("timer");

  let message = "";

  function getCurrentTimeString() {
    const currentTime = new Date();
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const seconds = currentTime.getSeconds();
    const timeString = `${hours}:${minutes}:${seconds}`;
    return timeString;
  }

  function displayMessage(username, message, className, isOnline) {
    const messageDiv = document.createElement("div");
    messageDiv.className = className;
    const onlineDotClass = isOnline ? "online" : "offline";
    messageDiv.innerHTML = `<span class="online-dot ${onlineDotClass}"></span><strong>${username}:</strong> ${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

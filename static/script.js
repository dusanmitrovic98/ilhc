document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatBox");
  const messageInput = document.getElementById("messageInput");
  const sendMessageBtn = document.getElementById("sendMessage");
  const audioPlayer = document.getElementById("audioPlayer");
  const timer = document.getElementById("timer");

  let message = "";

  function getCurrentTimeString() {
    const currentTime = new Date();

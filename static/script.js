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

  function generateRandomUsername() {
    const adjectives = ["Cuddly", "Fluffy", "Psycho", "Sunny", "Bubbly"];
    const animals = ["Kitten", "Puppy", "Bunny", "Duckling", "Panda"];
    const randomAdjective =
      adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomAnimal = animals[Math.floor(Math.random() * animals.length)];
    return `${randomAdjective} ${randomAnimal}`;
  }

  const USERNAME_ME = generateRandomUsername();
  const onlineUsers = {};
  onlineUsers[USERNAME_ME] = true;

  const socket = io.connect();
  socket.emit("connect_client", USERNAME_ME);

  socket.on("refresh_clients", () => {
    socket.emit("connect_client", USERNAME_ME);
  });

  function playAudio(songBuffer) {
    const blob = new Blob(songBuffer, { type: "audio/mp3" });
    const audioUrl = URL.createObjectURL(blob);
    audioPlayer.src = audioUrl;
    audioPlayer.controls = true;
  }

  function sendMessage() {
    message = messageInput.value;
    if (message.trim() !== "") {
      displayMessage(USERNAME_ME, message, "message");
      messageInput.value = "";

      fetch("/chat", {
        method: "POST",
        body: `message=${encodeURIComponent(USERNAME_ME + "|" + message)}`,
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      })
        .then((response) => response.text())
        .then((responseText) => {
          if (responseText != "") {
            displayMessage("Server", responseText, "server-message");
          }
        })
        .catch((error) => {
          console.error("Error sending message:", error);
        });
    }
  }

  function updateSongList(songs) {

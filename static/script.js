document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatBox");
  const messageInput = document.getElementById("messageInput");
  const sendMessageBtn = document.getElementById("sendMessage");
  const audioPlayer = document.getElementById("audioPlayer");

  let message = "";

  function getCurrentTimeString() {
    const currentTime = new Date();
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const seconds = currentTime.getSeconds();
    const timeString = `${hours}:${minutes}:${seconds}`;

    return timeString;
  }

  function displayMessage(username, message, className) {
    const isOnline = onlineUsers[username] || false;
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

  function displayMessage(username, message, className, isOnline) {
    const messageDiv = document.createElement("div");
    messageDiv.className = className;
    const onlineDotClass = isOnline ? "online" : "offline";
    messageDiv.innerHTML = `<span class="online-dot ${onlineDotClass}"></span><strong>${username}:</strong> ${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function playAudio(songBuffer) {
    const blob = new Blob(songBuffer, { type: "audio/mp3" });
    const audioUrl = URL.createObjectURL(blob);
    audioPlayer.src = audioUrl;
    audioPlayer.controls = true;
    audioPlayer.autoplay = true;
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

  messageInput.addEventListener("keydown", (event) => {
    if (event.keyCode === 13) {
      sendMessageBtn.click();
    }
  });

  sendMessageBtn.addEventListener("click", sendMessage);

  socket.on("update_online_users", (onlineUsersList) => {
    const onlineUsersElement = document.getElementById("onlineUsers");
    onlineUsersElement.innerHTML = "Online Users: " + onlineUsersList.message;
  });

  socket.on("play_song", (data) => {
    const songPath = `/stream/${data.song}`;
    const songBuffer = [];
    fetch(songPath)
      .then((response) => {
        const reader = response.body.getReader();
        return new ReadableStream({
          start(controller) {
            function pump() {
              return reader.read().then(({ done, value }) => {
                if (done) {
                  playAudio(songBuffer);

                  return;
                }
                songBuffer.push(value);
                pump();
              });
            }
            pump();
          },
        });
      })
      .catch((error) => {
        console.error("Error loading song:", error);
      });
  });

  socket.on("chat_message", (data) => {
    if (data.username == USERNAME_ME) {
    } else {
      displayMessage(data.username, data.message, "message");
    }
  });

  socket.on("clear_chat", () => {
    chatBox.innerHTML = "";
  });

  socket.on("play_song_from_start", () => {
    audioPlayer.currentTime = 0;
    audioPlayer.controls = true;
    audioPlayer.autoplay = true;
  });

  socket.on("song_pause", () => {
    audioPlayer.pause();
  });

  socket.on("song_resume", () => {
    audioPlayer.play();
  });

  setTimeout(function () {
    displayMessage("Server", "Welcome to the chat!", "server-message");
  }, 1000);
});

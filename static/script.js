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
    const songListElement = document.getElementById("song_list");
    songListElement.innerHTML = "";
    songs.forEach((song, index) => {
      const listItem = document.createElement("li");
      listItem.textContent = `${index + 1}. ${song} ❤️ `;
      songListElement.appendChild(listItem);
    });
  }

  messageInput.addEventListener("keydown", (event) => {
    if (event.keyCode === 13) {
      sendMessageBtn.click();
    }
  });

  sendMessageBtn.addEventListener("click", sendMessage);

  socket.on("update_online_users", (onlineUsersList) => {
    const onlineUsersElement = document.getElementById("onlineUsers");
    onlineUsersElement.innerHTML = "Online: " + onlineUsersList.message;
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
    if (data.username != USERNAME_ME) {
      displayMessage(data.username, data.message, "message");
    }
  });

  socket.on("fetch_chat_log", (data) => {
    if (data.connected_user == USERNAME_ME) {
      displayMessage(data.username, data.message, "message");
    } else {
      return;
    }
  });

  socket.on("clear_chat", () => {
    chatBox.innerHTML = "";
  });

  socket.on("clear_chat_user", (data) => {
    if (data.username != USERNAME_ME) {
      return;
    }
    chatBox.innerHTML = "";
  });

  socket.on("play_song_from_start", () => {
    audioPlayer.currentTime = 0;
    audioPlayer.controls = true;
    audioPlayer.autoplay = false;
  });

  socket.on("song_pause", () => {
    audioPlayer.pause();
  });

  socket.on("song_resume", () => {
    audioPlayer.play();
  });

  socket.on("set_song_current_time", (data) => {
    audioPlayer.currentTime = data.new_current_time;
  });

  socket.on("update_song_list", (data) => {
    updateSongList(data.songs);
  });

  socket.on("set_loop_flag", (data) => {
    audioPlayer.loop = data.loop_flag;
  });

  socket.on("set_autoplay_flag", (data) => {
    flag = data.autoplay_flag;
    audioPlayer.autoplay = flag;
    console.log(audioPlayer.autoplay);
  });

  socket.on("fetch_timestamp", (data) => {
    timestamp = audioPlayer.currentTime;
    if (data.username == USERNAME_ME) {
      socket.emit("timestamp_fetched", { timestamp: timestamp });
    }
  });

  setTimeout(function () {
    displayMessage("Server", "Welcome to the chat!", "message");
  }, 1000);
});

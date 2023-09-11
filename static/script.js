document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatBox");
  const messageInput = document.getElementById("messageInput");
  const sendMessageBtn = document.getElementById("sendMessage");
  const audioPlayer = document.getElementById("audioPlayer");

  function getCurrentTimeString() {
    // Create a new Date object to get the current time
    const currentTime = new Date();

    // Get the hours, minutes, and seconds
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const seconds = currentTime.getSeconds();

    // Format the time as a string
    const timeString = `${hours}:${minutes}:${seconds}`;

    return timeString;
  }

  let message = "";

  function displayMessage(username, message, className) {
    const isOnline = onlineUsers[username] || false;
    const messageDiv = document.createElement("div");
    messageDiv.className = className;
    const onlineDotClass = isOnline ? "online" : "offline";
    messageDiv.innerHTML = `<span class="online-dot ${onlineDotClass}"></span><strong>${username}:</strong> ${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Generate a random cute username
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
  // updateOnlineStatus();

  // Connect to the Socket.IO server
  const socket = io.connect();
  // socket.emit("connect", USERNAME_ME);
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

  // Function to handle audio playback
  function playAudio(songBuffer) {
    const blob = new Blob(songBuffer, { type: "audio/mp3" });
    const audioUrl = URL.createObjectURL(blob);
    audioPlayer.src = audioUrl;
    audioPlayer.controls = true;
    audioPlayer.autoplay = true;
  }

  // Function to send a message
  function sendMessage() {
    message = messageInput.value;
    if (message.trim() !== "") {
      displayMessage(USERNAME_ME, message, "message");
      messageInput.value = "";

      // Send the message to the server
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

  // Handle Enter key press in the message input field
  messageInput.addEventListener("keydown", (event) => {
    if (event.keyCode === 13) {
      // If Enter key is pressed, trigger the click event on the "Send" button
      sendMessageBtn.click();
    }
  });

  sendMessageBtn.addEventListener("click", sendMessage);

  // socket.on("connect", () => {
  //   const username = USERNAME_ME; // Change this to get the user's actual username
  //   onlineUsers[username] = true;
  //   // Update the user's online status in the chat
  //   // updateOnlineStatus();
  //   // Broadcast the updated online user list to all clients
  //   broadcastOnlineUsers();
  // });

  // function broadcastOnlineUsers() {
  //   const onlineUsersList = Object.keys(onlineUsers).filter(
  //     (username) => onlineUsers[username]
  //   );
  //   io.emit("update_online_users", onlineUsersList);
  // }

  socket.on("update_online_users", (onlineUsersList) => {
    // Update the list of online users in your UI
    const onlineUsersElement = document.getElementById("onlineUsers");
    onlineUsersElement.innerHTML = "Online Users: " + onlineUsersList.message;
  });

  // Listen for song playback command from the server
  socket.on("play_song", (data) => {
    const songPath = `/stream/${data.song}`;
    const songBuffer = []; // Initialize an array to hold the song chunks
    fetch(songPath)
      .then((response) => {
        const reader = response.body.getReader();
        return new ReadableStream({
          start(controller) {
            function pump() {
              return reader.read().then(({ done, value }) => {
                if (done) {
                  playAudio(songBuffer); // Start playback once the entire song is received

                  return;
                }
                songBuffer.push(value); // Append the chunk to the buffer
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

  // Listen for incoming chat messages from the server
  socket.on("chat_message", (data) => {
    if (data.username == USERNAME_ME) {
      // displayMessage(USERNAME_ME, data.message, "message");
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

  // Simulate receiving a welcome message from the server (for demonstration)
  setTimeout(function () {
    displayMessage("Server", "Welcome to the chat!", "server-message");
  }, 1000);
});

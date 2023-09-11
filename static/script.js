document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatBox");
  const messageInput = document.getElementById("messageInput");
  const sendMessageBtn = document.getElementById("sendMessage");
  const audioPlayer = document.getElementById("audioPlayer");

  // Generate a random cute username
  function generateRandomUsername() {
    const adjectives = ["Cuddly", "Fluffy", "Tiny", "Sunny", "Bubbly"];
    const animals = ["Kitten", "Puppy", "Bunny", "Duckling", "Panda"];
    const randomAdjective =
      adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomAnimal = animals[Math.floor(Math.random() * animals.length)];
    return `${randomAdjective} ${randomAnimal}`;
  }

  const USERNAME_ME = generateRandomUsername();

  let isOnline = true; // Set the initial online status

  // Connect to the Socket.IO server
  const socket = io.connect();

  // Function to display a message in the chat box
  function displayMessage(username, message, className) {
    const messageDiv = document.createElement("div");
    messageDiv.className = className;
    messageDiv.innerHTML = `<span class="online-dot ${
      isOnline ? "online" : "offline"
    }"></span><strong>${username}:</strong> ${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
  }

  // Function to append a message to the chat box
  function appendMessage(message) {
    const messageElement = document.createElement("p");
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Function to send a message
  function sendMessage() {
    const message = messageInput.value;
    if (message.trim() !== "") {
      // appendMessage(`You: ${message}`);
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

  // Listen for song playback command from the server
  socket.on("play_song", (data) => {
    const songPath = `/stream/${data.song}`;
    audioPlayer.src = songPath;
    audioPlayer.controls = true;
    audioPlayer.autoplay = true;
  });

  // Listen for incoming chat messages from the server
  socket.on("chat_message", (data) => {
    if (data.username == USERNAME_ME) {
      // displayMessage(USERNAME_ME, data.message, "message");
    } else {
      displayMessage(data.username, data.message, "message");
    }
  });

  // Simulate receiving a welcome message from the server (for demonstration)
  setTimeout(function () {
    displayMessage("Server", "Welcome to the chat!", "server-message");
  }, 1000);
});

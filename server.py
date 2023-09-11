from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
import os

app = Flask(__name__)
socketio = SocketIO(app)

music_folder = "music"  # Change this to the path of your music folder.

chat_messages = []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/stream/<song>')
def stream(song):
    song_path = os.path.join(music_folder, song)
    return Response(generate_audio(song_path), mimetype="audio/mpeg")

def generate_audio(song_path):
    with open(song_path, "rb") as audio_file:
        while True:
            audio_chunk = audio_file.read(1024)
            if not audio_chunk:
                break
            yield audio_chunk

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form.get('message').split('|')[0]
    message = request.form.get('message').split('|')[1]
    if message:
        if message == '/list':
            songs = os.listdir(music_folder)
            song_list = "\n".join([f"{i + 1}. {song} ❤️ " for i, song in enumerate(songs)])
            return song_list
        elif message.startswith('/play ') or message.startswith('/p ') or message.startswith('/ '):
            try:
                song_number = int(message.split(' ')[1])
                songs = os.listdir(music_folder)
                if 1 <= song_number <= len(songs):
                    song_to_play = songs[song_number - 1]
                    socketio.emit("play_song", {"song": song_to_play})
                    return song_to_play
                else:
                    return "Invalid song number."
            except ValueError:
                return "Invalid command format."
        else:
            # Add the user's message to the chat_messages list
            chat_messages.append(message)
            # Broadcast the message to all connected clients
            socketio.emit('chat_message', {'username': username, 'message': message})
            return ""
    return "Invalid command."

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from pytube.cli import on_progress
from pytube import YouTube
import sys
import os

app = Flask(__name__)
socketio = SocketIO(app)

NAME_SERVER = "Server"

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
            audio_chunk = audio_file.read(4096)
            if not audio_chunk:
                break
            yield audio_chunk

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form.get('message').split('|')[0]
    message = request.form.get('message').split('|')[1]
    if message:
        if message == "/clear":
            clear_chat(username)
        elif message == '/list':
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
                    socketio.emit("chat_message", {"username": "Server", "message": "Buffering \"" + song_to_play + "\"..."})
                    return ""
                else:
                    return "Invalid song number."
            except ValueError:
                return "Invalid command format."
        elif message.startswith('/download '):
            url = message.split(' ')[1]
            print(url)
            download_from_url(url)
        else:
            # Add the user's message to the chat_messages list
            chat_messages.append(message)
            # Broadcast the message to all connected clients
            socketio.emit('chat_message', {'username': username, 'message': message})
            return ""
    return ""

def clear_chat(username):
    socketio.emit("clear_chat")
    socketio.emit("chat_message", {"username": "Server", "message": username + " cleared the chat..."})

def download_from_url(url):
    socketio.emit("chat_message", {"username": "Server", "message": url})
    youtube = YouTube(url, on_progress_callback=on_progress)
    out_file = youtube.streams.filter(only_audio=True).first().download(music_folder)
    os.rename(out_file, os.path.splitext(out_file)[0] + ".mp3")
    server_response('"' + os.path.basename(os.path.splitext(out_file)[0] + ".mp3") + '" downloaded successfully.')
    
def server_response(response):
    socketio.emit("chat_message", {"username": NAME_SERVER, "message": response})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

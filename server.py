from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from pytube.cli import on_progress
from pymongo import MongoClient
from datetime import datetime
from pytube import YouTube
import sys
import os

app = Flask(__name__)
socketio = SocketIO(app)

# MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client['ilhchat'] 
collection_messages = db["messages"]

# Constants
NAME_SERVER = "Server"
MUSIC_FOLDER = "music"
COMMANDS = {
        '/online': 'Lists online users.',
        '/list': 'Lists all songs.',
        '/play song_number': 'Plays a specific song.',
        '/p song_number': 'Plays a specific song (shortcut).',
        '/ song_number': 'Plays a specific song (shortcut).',
        '/download song_url': 'Downloads a song from a URL.',
        '/rename song_number new_name.mp3': 'Renames a song.',
        '/songtime seconds': 'Sets the current time of the song.',
        '/start': 'Starts playing the song from the beginning.',
        '/pause': 'Pauses the currently playing song.',
        '/resume': 'Resumes the paused song.',
        '/clear': 'Clears the chat.'
    }

# Data storage
chat_messages = []
connected_clients = []

# Helper functions
def server_response(response):
    socketio.emit("chat_message", {"username": NAME_SERVER, "message": response})

def clear_chat(username):
    socketio.emit("clear_chat")
    server_response(f"{username} cleared the chat...")

def list_all_songs():
    songs = os.listdir(MUSIC_FOLDER)
    for i, song in enumerate(songs, start=1):
        server_response(f"{i}. {song} ❤️ ")

def play_song_from_start():
    socketio.emit("play_song_from_start")

def song_pause():
    socketio.emit("song_pause")

def song_resume():
    socketio.emit("song_resume")

def play_song(message):
    try:
        song_number = int(message.split(' ')[1])
        songs = os.listdir(MUSIC_FOLDER)
        if 1 <= song_number <= len(songs):
            song_to_play = songs[song_number - 1]
            socketio.emit("play_song", {"song": song_to_play})
            server_response(f'Buffering "{song_to_play}"...')
            return ""
        else:
            return "Invalid song number."
    except ValueError:
        return "Invalid command format."

def rename_song(message):
    try:
        song_number = int(message.split(' ')[1])
        new_name = message.split(' ')[2]
        songs = os.listdir(MUSIC_FOLDER)
        if 1 <= song_number <= len(songs):
            old_name = songs[song_number - 1]
            old_path = os.path.join(MUSIC_FOLDER, old_name)
            new_path = os.path.join(MUSIC_FOLDER, new_name)
            try:
                os.rename(old_path, new_path)
                server_response(f'Song "{old_name}" renamed to "{new_name}"')
            except OSError as e:
                server_response(f'Error renaming song: {str(e)}')
            return ""
        else:
            return "Invalid song number."
    except ValueError:
        return "Invalid command format."

def set_song_current_time(message):
    new_current_time = int(message.split(' ')[1])
    socketio.emit("set_song_current_time", {"new_current_time": new_current_time})

def download_from_url(message):
    url = message.split(' ')[1]
    socketio.emit("chat_message", {"username": NAME_SERVER, "message": url})
    youtube = YouTube(url, on_progress_callback=on_progress)
    out_file = youtube.streams.filter(only_audio=True).first().download(MUSIC_FOLDER)
    os.rename(out_file, os.path.splitext(out_file)[0] + ".mp3")
    server_response(f'"{os.path.basename(os.path.splitext(out_file)[0] + ".mp3")}" downloaded successfully.')

def help():
    global COMMANDS

    for command, description in COMMANDS.items():
        server_response(f'{command}: {description}')

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    server_response("User connected.")

@socketio.on("disconnect")
def handle_disconnect():
    global connected_clients
    connected_clients = []
    socketio.emit("refresh_clients")
    server_response("User disconnected.")

@socketio.on("connect_client")
def connect_client(username):
    global connected_clients
    connected_clients.append(username)
    connected_clients = list(set(connected_clients))
    response_clients = ' ❤️ '.join(connected_clients)
    socketio.emit('update_online_users', {'message': response_clients})
    
    # Fetch the last 20 chat messages from MongoDB, sorted by timestamp in descending order
    chat_history = collection_messages.find().sort('timestamp', -1).limit(20)

    # Reverse the order to get the messages in ascending order
    chat_history = list(chat_history)[::-1]

    # Emit the chat messages to the connected user
    for chat_entry in chat_history:
        socketio.emit("fetch_chat_log", {"connected_user": username, "username": chat_entry['username'], "message": chat_entry['message']})

@app.route('/stream/<song>')
def stream(song):
    song_path = os.path.join(MUSIC_FOLDER, song)
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
    global COMMANDS

    username, message = request.form.get('message').split('|')
    command_keys = COMMANDS.keys()

    # Check if the message does not start with any of the command keys
    if message and not any(message.startswith(key) for key in command_keys):
        chat_entry = {
            'username': username,
            'message': message,
            'timestamp': datetime.now()
        }
        collection_messages.insert_one(chat_entry)
    if message:
        chat_messages.append(message)
        if message == "/clear":
            clear_chat(username)
        elif message == "/online":
            global connected_clients
            connected_clients = []
            socketio.emit("refresh_clients")
        elif message == "/start":
            play_song_from_start()
        elif message == "/help":
            help()
        elif message == "/pause":
            song_pause()
        elif message == "/resume":
            song_resume()
        elif message.startswith("/rename "):
            rename_song(message)
        elif message == '/list':
            list_all_songs()
        elif message.startswith('/play ') or message.startswith('/p ') or message.startswith('/ '):
            play_song(message)
        elif message.startswith('/download '):
            download_from_url(message)
        elif message.startswith('/songtime '):
            set_song_current_time(message)
    return ""

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

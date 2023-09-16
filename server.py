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

# Flags
autoplay_mem = False
loop_mem = False
sync_timestamp = 0
sync_timestamp_username = ""

# Constants
NAME_SERVER = "Server"
MUSIC_FOLDER = "music"
COMMANDS = {
        '/users': 'Lists all online users and their numbers.',
        '/online': 'Refreshes online users display.',
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
        '/clear': 'Clears the chat.',
        '/loop on/off': 'Looping enabled/disabled.',
        '/autoplay on/off': 'Autoplay enabled/disabled.',
        '/sync user_number': 'Syncs with the timestamp of the user under. Order "/online"... "/users"... "/sync users_number"',
        '/s user_number': 'Syncs with the timestamp of the user under. Order "/online"... "/users"... "/sync users_number"',
        '/timestamp user_number': 'Fetches user timestamp. Order "/online"... "/users"... "/timestamp users_number"',
        '/ts user_number': 'Fetches user timestamp. Order "/online"... "/users"... "/timestamp users_number"',
    }

# Data storage
chat_messages = []
connected_clients = []

def get_song_list():
    songs = os.listdir(MUSIC_FOLDER)
    return songs

# Helper functions
socketio.on("server_response")
def server_response(response):
    socketio.emit("chat_message", {"username": NAME_SERVER, "message": response})

def clear_chat(username):
    socketio.emit("clear_chat")
    server_response(f"{username} cleared the chat...")

def list_all_songs():
    songs = get_song_list()
    socketio.emit("update_song_list", {"songs": songs})

def play_song_from_start():
    socketio.emit("play_song_from_start")

def song_pause():
    socketio.emit("song_pause")

def song_resume():
    socketio.emit("song_resume")

def play_song(message):
    try:
        songs = os.listdir(MUSIC_FOLDER)
        if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
        song_number = int(message.split(' ')[1])
        if 1 <= song_number <= len(songs):
            song_to_play = songs[song_number - 1]
            socketio.emit("play_song", {"song": song_to_play})
            server_response(f'Buffering "{song_to_play}"...')
            return ""
        else:
            server_response("Invalid song number.")
    except ValueError:
        server_response("Invalid command format.")
        return

def rename_song(message):
    try:
        if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
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
                list_all_songs()
            except OSError as e:
                server_response(f'Error renaming song: {str(e)}')
            return ""
        else:
            return "Invalid song number."
    except ValueError:
        server_response("Invalid command format.")
        return

def set_song_current_time(message):
    try:
        if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
        new_current_time = int(message.split(' ')[1])
        socketio.emit("set_song_current_time", {"new_current_time": new_current_time})
    except ValueError:
        server_response("Invalid command format.")
        return
    
def download_from_url(message):
    try:
        if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
        url = message.split(' ')[1]
        socketio.emit("chat_message", {"username": NAME_SERVER, "message": url})
        youtube = YouTube(url, on_progress_callback=on_progress)
        out_file = youtube.streams.filter(only_audio=True).first().download(MUSIC_FOLDER)
        os.rename(out_file, os.path.splitext(out_file)[0] + ".mp3")
        server_response(f'"{os.path.basename(os.path.splitext(out_file)[0] + ".mp3")}" downloaded successfully.')
        list_all_songs()
    except ValueError:
        server_response("Invalid command format.")
        return

def help():
    global COMMANDS
    for command, description in COMMANDS.items():
        server_response(f'{command}: {description}')

def sync_timestamp(message):
    global sync_timestamp_username
    if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
    user_number = int(message.split(' ')[1])
    username = connected_clients[user_number - 1]
    sync_timestamp_username = username
    socketio.emit("sync_timestamp", {'username': username})

def fetch_timestamp(message):
    global sync_timestamp_username
    if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
    user_number = int(message.split(' ')[1])
    username = connected_clients[user_number - 1]
    sync_timestamp_username = username
    socketio.emit("fetch_timestamp", {'username': username})

def loop(message):
    global loop_mem
    try:
        if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
        loop_flag = message.split(' ')[1]
        if loop_flag == 'on':
            socketio.emit("set_loop_flag", { "loop_flag": True })
            loop_mem = True
            server_response('Looping enabled.')
        elif loop_flag == 'off':
            socketio.emit("set_loop_flag", { "loop_flag": False })
            loop_mem = False
            server_response('Looping disabled.')
    except ValueError:
        server_response("Invalid command format.")
        return
    
# socketio.on("fetch_chat_history")
def fetch_chat_history(username):
    chat_history = collection_messages.find().sort('timestamp', -1).limit(20)
    chat_history = list(chat_history)[::-1]
    socketio.emit("clear_chat_user", {'username': username})
    for chat_entry in chat_history:
        socketio.emit("fetch_chat_log", {"connected_user": username, "username": chat_entry['username'], "message": chat_entry['message']})

def list_users():
    i = 1
    for user in connected_clients:
        server_response(f'{i}. {user}')
        i += 1

def autoplay(message):
    global autoplay_mem
    try:
        if len(message.split(' ')) <= 1:
            server_response("Invalid command format.")
            return
        autoplay_flag = message.split(' ')[1]
        if autoplay_flag == 'on':
            socketio.emit("set_autoplay_flag", { "autoplay_flag": True })
            autoplay_mem = True
            server_response('Autoplay enabled.')
        elif autoplay_flag == 'off':
            socketio.emit("set_autoplay_flag", { "autoplay_flag": False })
            autoplay_mem = False
            server_response('Autoplay disabled.')
    except ValueError:
        server_response("Invalid command format.")
        return

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("timestamp_synced")
def timestamp_fetched(data):
    global sync_timestamp, sync_timestamp_username
    server_response(str(data))
    socketio.emit("sync_users", {"username": sync_timestamp_username, "timestamp": data})

@socketio.on("timestamp_fetched")
def timestamp_fetched(data):
    global sync_timestamp, sync_timestamp_username
    server_response(str(data))
    socketio.emit("sync_users", {"username": sync_timestamp_username, "timestamp": data})

@socketio.on("sync_users")
def sync_users(timestamp):
    socketio.emit("sync_users", { "timestamp": timestamp})
    server_response("Users synced.")

@socketio.on("song_ready")
def song_ready(data):
    if 'username' in data:
        username = data['username']
    server_response(f'{username} is ready.')

@socketio.on("connect")
def handle_connect():
    server_response("User connected.")
    list_all_songs()

@socketio.on("disconnect")
def handle_disconnect():
    global connected_clients
    connected_clients = []
    socketio.emit("refresh_clients")
    server_response("User disconnected.")

@socketio.on("connect_client")
def connect_client(username):
    global connected_clients
    # fetch_chat_history(username)
    connected_clients.append(username)
    connected_clients = list(set(connected_clients))
    response_clients = ' ❤️ '.join(connected_clients)
    socketio.emit('update_online_users', {'message': response_clients}) # todo update_online_users !!!
    socketio.emit("set_autoplay_flag", { "autoplay_flag": autoplay_mem })
    socketio.emit("set_loop_flag", { "loop_flag": loop_mem })

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
        elif message.startswith('/loop '):
            loop(message)
        elif message.startswith('/autoplay '):
            autoplay(message)
        elif message.startswith('/users'):
            list_users()
        elif message.startswith('/sync ') or message.startswith('/s '):
            sync_timestamp(message)
        # elif message.startswith('/sync '):
        #     sync_user(message)
            
    socketio.emit("chat_message", { "username": username, "message": message })

        # Check if the message does not start with any of the command keys
    if message and not any(message.startswith(key.split(' ')[0]) for key in command_keys):
        chat_entry = {
            'username': username,
            'message': message,
            'timestamp': datetime.now()
        }
        collection_messages.insert_one(chat_entry)
    return ""

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

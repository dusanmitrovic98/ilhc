from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from pytube.cli import on_progress
from pytube import YouTube
import sys
import os

app = Flask(__name__)
socketio = SocketIO(app)

NAME_SERVER = "Server"

music_folder = "music"

chat_messages = []
connected_clients = []

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    server_response("User connected.")

@socketio.on("disconnect")
def handle_connect():
    global connected_clients
    connected_clients = []
    socketio.emit("refresh_clients")
    server_response("User disconnected.")

@socketio.on("connect_client")
def connect_client(username):
    global connected_clients
    connected_clients.append(username)
    connected_clients = list(set(connected_clients))
    print(connected_clients[0])
    response_clients = ''
    for client in connected_clients:
        response_clients += client + " ❤️ "
    socketio.emit('update_online_users', {'message': response_clients[0:len(response_clients) - 4]})

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
        elif message == "/online":
            global connected_clients
            connected_clients = []
            socketio.emit("refresh_clients")
        elif message == "/start":
            play_song_from_start()
        elif message == "/help":
            help()

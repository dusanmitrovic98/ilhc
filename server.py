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

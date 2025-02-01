import threading
import time
from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from pytube.cli import on_progress
from pymongo import MongoClient
from datetime import datetime
from moviepy.editor import AudioFileClip
from pytube import YouTube
import sys
import os
import random

available_songs = []  # Add your available songs to this list
is_random_playing = False
allrandom = True
song_path = "C:/Users/BK2O198/Documents/Workstation/ilhchat/music/sia_snowman.mp3"

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
        # '/download song_url': 'Downloads a song from a URL.',
        '/rename song_number new_name.mp3': 'Renames a song.',
        '/songtime seconds': 'Sets the current time of the song.',
        '/start': 'Starts playing the song from the beginning.',

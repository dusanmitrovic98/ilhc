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
        '/pause': 'Pauses the currently playing song.',
        '/resume': 'Resumes the paused song.',
        '/clear': 'Clears the chat.',
        '/loop on/off': 'Looping enabled/disabled.',
        '/autoplay on/off': 'Autoplay enabled/disabled.',
        '/allrandom on/off': 'Allrandom enabled/disabled.',
        '/sync user_number': 'Syncs with the timestamp of the user under. Order "/online"... "/users"... "/sync users_number"',
        '/s user_number': 'Syncs with the timestamp of the user under. Order "/online"... "/users"... "/sync users_number"',
        '/timestamp user_number': 'Fetches user timestamp. Order "/online"... "/users"... "/timestamp users_number"',
        '/ts user_number': 'Fetches user timestamp. Order "/online"... "/users"... "/timestamp users_number"',
        '/random': 'Plays random song. If allrandom is enabled it will continue to play new random songs each time song is finished.',

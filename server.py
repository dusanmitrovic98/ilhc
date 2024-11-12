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

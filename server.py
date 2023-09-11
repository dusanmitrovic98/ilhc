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

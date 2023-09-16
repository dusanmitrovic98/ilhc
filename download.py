from pytube import YouTube
from pytube.cli import on_progress
import os

MUSIC_FOLDER = 'music'

def download_from_url(url):
    try:
        youtube = YouTube(url, on_progress_callback=on_progress)
        out_file = youtube.streams.filter(only_audio=True).first().download(MUSIC_FOLDER)
        os.rename(out_file, os.path.splitext(out_file)[0] + ".mp3")
    except ValueError:
        print("Invalid command format.")
    
video_url = ''    

download_from_url(video_url)
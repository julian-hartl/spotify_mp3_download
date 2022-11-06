#!/usr/bin/python
import argparse
import os
import subprocess
import sys
from dataclasses import dataclass

import yt_dlp
from youtubesearchpython import VideosSearch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

auth_manager = SpotifyClientCredentials()
access_token = auth_manager.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=access_token)

temp_dir = ".temp"


@dataclass
class VideoResult:
    name: str
    url: str
    id: str


def search_videos(queries: [str]) -> [str]:
    return list(map(search_video, queries))


def search_video(query: str) -> VideoResult:
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    video = result.get("result")[0]
    video_id = video["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    return VideoResult(name=video.get("title"), url=url, id=video_id)


def get_song_names(playlist_id: str) -> [str]:
    result = sp.playlist(playlist_id=playlist_id)
    names = []
    for track_json in result['tracks']['items']:
        track = track_json['track']
        name = f"{track['artists'][0]['name']} - {track['name']}"
        names.append(name)
    return names


def download_mp3s(urls: [str]):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'.temp/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


def filter_songs(ids: [str], output_path: str) -> [str]:
    os.system(f"mkdir -p {output_path}")
    output = subprocess.check_output(f"ls {output_path}", shell=True).decode("utf-8")
    file_list = output.split("\n")
    return filter(lambda song: f"{song}.mp3" not in file_list, ids)


def main():
    parser = argparse.ArgumentParser(
        prog='Spotify MP3 Downloader',
        description='Downloads songs from a spotify playlist as mp3 files',
    )
    parser.add_argument('playlist_id')
    parser.add_argument('-o', '--output', default="out")
    args = parser.parse_args()
    playlist_id = args.playlist_id
    output_path = args.output
    print(f"Getting songs from playlist {playlist_id}...")
    song_names = get_song_names(playlist_id=playlist_id)
    print(f"Got {len(song_names)} songs from playlist")
    songs = list(filter_songs(song_names, output_path=output_path))
    amount_of_songs = len(songs)
    if amount_of_songs == 0:
        print("Local playlist is in sync with spotify playlist")
    else:
        print(f"Getting {len(song_names) - amount_of_songs} songs from cache...")
    if amount_of_songs > 0:
        os.system(f"mkdir {temp_dir}")
        print(f"Downloading {amount_of_songs} songs")
        for song in songs:
            result = search_video(song)
            print(f"Downloading {result.name}")
            download_mp3s([result.url])
            os.system(f'mv "{temp_dir}/{result.id}.mp3" "{output_path}/{song}.mp3"')
        print(f"Downloaded {amount_of_songs} songs")
        print("Cleaning up temp files...")
        os.system(f"rm -r {temp_dir}")
    print("Done")


main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

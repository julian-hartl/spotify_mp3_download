#!/usr/bin/python
import argparse
import os
import subprocess
from dataclasses import dataclass

import spotipy
import yt_dlp
from uuid import uuid4
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch

load_dotenv()
auth = SpotifyOAuth(redirect_uri="http://localhost:8888/callback", scope="playlist-read-private")
accessToken = auth.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=accessToken)

temp_dir = f".{uuid4()}"


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


def get_song_names(id: str, type: str) -> [str]:
    names = []
    if type == "playlist":
        result = sp.playlist(playlist_id=id)
        for track_json in result['tracks']['items']:
            track = track_json['track']
            name = build_song_name(track['artists'][0]['name'], track['name'])
            names.append(name)
    if type == "album":
        result = sp.album(album_id=id)
        for track in result['tracks']['items']:
            name = build_song_name(track['artists'][0]['name'], track['name'])
            names.append(name)

    return names


def build_song_name(artist: str, song_name: str) -> str:
    name = f"{artist} - {song_name}"
    return name


def download_mp3s(urls: [str]):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{temp_dir}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


def filter_songs(ids: [str], output_path: str) -> [str]:
    os.system(f'mkdir -p "{output_path}"')
    output = subprocess.check_output(f'ls "{output_path}"', shell=True).decode("utf-8")
    file_list = output.split("\n")
    return filter(lambda song: f"{song}.mp3" not in file_list, ids)


def createDir(path: str):
    os.system(f'mkdir -p "{path}"')


def main():
    parser = argparse.ArgumentParser(
        prog='Spotify MP3 Downloader',
        description='Downloads songs from a spotify playlist as mp3 files',
    )
    parser.add_argument('id')
    parser.add_argument('-o', '--output', default="out")
    parser.add_argument('-t', '--type', default="playlist", choices=["album", "playlist"])
    args = parser.parse_args()
    id = args.id
    type = args.type
    output_path = args.output
    song_names = get_song_names(id, type)
    print(f"Got {len(song_names)} songs from {type}")
    songs = list(filter_songs(song_names, output_path=output_path))
    amount_of_songs = len(songs)
    if amount_of_songs == 0:
        print("Local playlist is in sync with spotify playlist")
    else:
        print(f"Getting {len(song_names) - amount_of_songs} songs from cache...")
    if amount_of_songs > 0:
        createDir(temp_dir)
        print(f"Downloading {amount_of_songs} songs")
        createDir(output_path)
        for song in songs:
            result = search_video(song)
            print(f"Downloading {result.name}")
            download_mp3s([result.url])
            os.system(f'mv "{temp_dir}/{result.id}.mp3" "{output_path}/{song}.mp3"')
        print(f"Downloaded {amount_of_songs} songs")
        print("Cleaning up temp files...")
        os.system(f'rm -r "{temp_dir}"')
    print("Done")


main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

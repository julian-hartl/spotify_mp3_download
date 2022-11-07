# Spotify MP3 Downloader

## Setup

1. Install [Python 3](https://www.python.org/downloads/)
2. Run ```pip install -r requirements.txt```
3. Install ffmpeg

```shell
brew install ffmpeg
```

4. Get your spotify client id and
   secret [here](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/)
5. Add .env file with the obtained values:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

6. Run ```python main.py <playlist_id>```

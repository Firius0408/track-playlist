# Spotify Track Playlist

Simple python script to track users playlists for new song updates and update a playlist with these songs

## Setup

This project uses Python >=3.6 and pipenv

Spotify API keys, playlist ID, and refresh token should be placed in `.env`:

`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_USER_REFRESH_TOKEN`, and `SPOTIFY_TRACK_PLAYLIST_ID`

The users to be tracked should be placed `data.json` as a list under `users`

```python
python3 -m pip install pipenv
pipenv install
```

## Tracking Playlist

The `track-playlist.py` script scans for songs and playlists added or created since the last runtime

`pipenv run python3 track-playlist.py`

Copyright © Brian Cheng 2021

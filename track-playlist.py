import spotifywebapi
import sys
import json
import datetime
import os
from concurrent.futures import ThreadPoolExecutor, wait

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID') 
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('SPOTIFY_USER_REFRESH_TOKEN')
TRACK_PLAYLIST_ID = os.getenv('SPOTIFY_TRACK_PLAYLIST_ID')

if CLIENT_ID or CLIENT_SECRET or REFRESH_TOKEN or TRACK_PLAYLIST_ID:
    pass
else:
    print('Missing env variable!', file=sys.stderr)
    exit(1)

def runUser(us):
    print('Starting user %s' % us)
    try:
        user = sp.getUser(us)
    except:
        print('Error with user %s: %s' % (us, sys.exc_info()[1]), file=sys.stderr)
        return
    try:
        playlists = sp.getUserPlaylists(user)
    except:
        print('Error with user %s playlists: %s' % (us, sys.exc_info()[1]), file=sys.stderr)
        return

    print('Finished pulling playlists for user %s' % us)
    futures = []
    for playlist in playlists:
        if "Top Songs " in playlist['name'] or playlist['owner']['id'] != us:
            continue

        futures.append(executor.submit(addTrackUris, playlist))

    wait(futures)
    print('Finished pulling tracks for user %s' % us)

def addTrackUris(playlist):
    try:
        tracks = sp.getTracksFromItem(playlist)
    except spotifywebapi.SpotifyError as err:
        print(err)
        return

    temptracks.extend(tracks)

if __name__ == '__main__':
    with open(sys.path[0] + '/data.json', 'r') as f:
        data = json.load(f)
else:
    with open('./data.json', 'r') as f:
        data = json.load(f)

print('Starting at %s ' % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
try:
    offset = datetime.datetime.fromisoformat(data['timestamp'])
except KeyError:
    print('No timestamp found in data.json, setting offset and exiting...', file=sys.stderr)
    data['timestamp'] = datetime.datetime.utcnow().isoformat()
    if __name__ == '__main__':
        with open(sys.path[0] + '/data.json', 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '))
    else:
        with open('./data.json', 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '))
    exit(1)
except ValueError:
    print('Incorrectly formatted timestamp found in data.json, exiting...', file=sys.stderr)
    exit(1)

print('Using UTC offset %s' % offset.strftime("%Y-%m-%d %H:%M:%S"))
data['timestamp'] = datetime.datetime.utcnow().isoformat()
try:
    users = data['users']
except KeyError:
    print("Could not find 'users' in data.json, exiting...", file=sys.stderr)
    exit(1)

sp = spotifywebapi.Spotify(CLIENT_ID, CLIENT_SECRET)
executor = ThreadPoolExecutor()
futures = []
temptracks = []
for user in users:
    futures.append(executor.submit(runUser, user))

wait(futures)
print('Finished pulling data')
executor.shutdown()
trackuris = [track['track']['uri'] for track in temptracks if datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ') > offset and track['track'] is not None and track['track']['id'] is not None]
if trackuris:
    trackurisset = set(trackuris)
    me = sp.getAuthUser(REFRESH_TOKEN)
    playlist = sp.getPlaylistFromId(TRACK_PLAYLIST_ID)
    playlisttracks = sp.getTracksFromItem(playlist)
    playlisttracksset = {i['track']['uri'] for i in playlisttracks}
    newtracksset = trackurisset - playlisttracksset
    if (newtracksset):
        me.addSongsToPlaylist(TRACK_PLAYLIST_ID, list(newtracksset))
    else:
        print('No change')
else:
    print('No change')
if __name__ == '__main__':
    with open(sys.path[0] + '/data.json', 'w') as f:
        json.dump(data, f, indent=4, separators=(',', ': '))
else:
    with open('./data.json', 'w') as f:
        json.dump(data, f, indent=4, separators=(',', ': '))

print('\nFinished at %s\n' % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

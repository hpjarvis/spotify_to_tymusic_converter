import json
import os
import requests

def create_secrets(filepath = './files/secrets.json'):
    data = {"Spotify": {"id": "", "secret": ""}, "Youtube": ""}
    os.makedirs("files")
    with open("./files/secrets.json", 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_secrets(filepath = './files/secrets.json') -> dict:
    with open(filepath) as f:
        d = json.load(f)
        return d

def get_all_tracks(tracks_endpoint, headers, playlist_tracks = []):
    tracks_callback = requests.get(tracks_endpoint, headers=headers)
    tracks_json = tracks_callback.json()
    total_tracks = tracks_json['total']

    for item in tracks_json['items']:
        item = item['track']

        track_artists = []
        for artist in item['artists']:
            track_artists.append(artist["name"])
        
        playlist_tracks.append({"Name": item["name"], "Artist": track_artists})

    if tracks_json['next'] != None:
        get_all_tracks(tracks_json['next'], headers, playlist_tracks)

    return (total_tracks, playlist_tracks)

def write_playlist_content(file_content, directory = "./playlists", missing_list = False):
    name_sufix = " errors.json" if missing_list else ".json"
    
    filepath = os.path.join(directory, file_content['name'] + name_sufix)
    with open(filepath, 'w') as f:
        json.dump(file_content, f, ensure_ascii=False, indent=4)
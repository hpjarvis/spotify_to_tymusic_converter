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

def search_and_add_track(ytmusic, index, playlist_id, playlist_tracks, playlist_contents, missing_items):
    print("\t{} - {}".format(index + 1, playlist_tracks[index]))
    search_results = ytmusic.search("{} {}".format(playlist_tracks[index]["Name"], playlist_tracks[index]["Artist"][0]), filter="songs", ignore_spelling=True)
    
    # append the tracks to the playlists_content tracks list
    playlist_contents["tracks"].append({"Name": playlist_tracks[index]["Name"], "Artist": playlist_tracks[index]["Artist"][0]})

    if search_results != []:
        search_result = search_results[0]
        print("\t\t YT Search: {} - {}".format(search_result['title'], search_result['artists'][0]['name']))

        try:
            ytmusic.add_playlist_items(playlist_id, [search_result['videoId']])

        except:
            print("Cannot add song - request timeout")

    else:
        print("\t\tCannot be found")
        missing_items["tracks"].append({"Name": playlist_tracks[index]["Name"], "Artist": playlist_tracks[index]["Artist"][0]})


def create_youtube_playlist(ytmusic, total_tracks, playlist_name):
    playlist_id = ytmusic.create_playlist(playlist_name, "created using spotifyt tool by hpjarvis")

    playlist_contents = {}
    playlist_contents["name"] = playlist_name
    playlist_contents["id"] = playlist_id
    playlist_contents["number of tracks"] = total_tracks
    playlist_contents["tracks"] = []

    missing_items = {}
    missing_items["name"] = playlist_name
    missing_items["tracks"] = []

    return playlist_contents, missing_items, playlist_id
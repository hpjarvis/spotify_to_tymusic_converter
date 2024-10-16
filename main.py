import os
import sys
import helpers
import requests
from datetime import datetime
from get_auth import run_auth_server
from ytmusicapi import YTMusic, setup_oauth
import ytmusicapi
import json

# check if the secrets file can be found
if not os.path.exists(os.path.join(os.getcwd(), 'files', 'secrets.json')):
    print("Closing: Cannot find secrets file, making template now")
    helpers.create_secrets()

    sys.exit()

if not os.path.exists(os.path.join(os.getcwd(), 'files', 'access_token.json')):
    print("Cannot find access_token.json, creating now")
    run_auth_server()

if not os.path.exists(os.path.join(os.getcwd(), 'files', 'yt_access_tokens.json')):
    print("Cannot find yt_access_token.json, creating now")
    setup_oauth("./files/yt_access_tokens.json")

if not os.path.exists(os.path.join(os.getcwd(), 'playlists')):
    print("Cannot find playlists folder, creating now")
    os.mkdir(os.path.join(os.getcwd(), 'playlists'))

if not os.path.exists(os.path.join(os.getcwd(), 'errors')):
    print("Cannot find errors folder, creating now")
    os.mkdir(os.path.join(os.getcwd(), 'errors'))

print("Reading access token")
access_token_file = helpers.load_secrets("./files/access_token.json")

if access_token_file['timestamp'] + access_token_file['expires_in'] < datetime.now().timestamp():
    print("access token expired, refreshing")
    run_auth_server()

print("Connecting to youtube music")
ytmusic = YTMusic("./files/yt_access_tokens.json")

# make the headers for the future requests using the access token
headers = {"Authorization": "Bearer " + access_token_file['access_token']}

# we need to collect the users user name and details
me_endpoint = "https://api.spotify.com/v1/me"
me_callback = callback = requests.get(me_endpoint, headers=headers)
me_callback_json = callback.json()

# we need a new endpoint to request user details
endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(me_callback_json['id'])

# make the sportify request header
print("Requesting playlists from spotify account")
callback = requests.get(endpoint, headers=headers)
callback_json = callback.json()
playlists = callback_json['items']

print("Requesting playlists from ytmusic account")
yt_playlists = ytmusic.get_library_playlists()
yt_playlist_names = [d['title'] for d in yt_playlists]

print("Found {} playlists:".format(len(playlists)))
for playlist in playlists:
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    tracks_endpoint = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

    if playlist_name in yt_playlist_names:
        print('Playlist already exists, skipping...')
        continue

    total_tracks, playlist_tracks = helpers.get_all_tracks(tracks_endpoint=tracks_endpoint, headers=headers, playlist_tracks=[])
    
    print("'{}' ({}) - {} songs - extracted {}".format(playlist_name, playlist_id, total_tracks, len(playlist_tracks)))
    print("Making playlist on yt music")

    playlist_id = ytmusic.create_playlist(playlist_name, "created using spotifyt tool by hpjarvis")

    playlist_contents = {}
    playlist_contents["name"] = playlist_name
    playlist_contents["id"] = playlist_id
    playlist_contents["number of tracks"] = total_tracks
    playlist_contents["tracks"] = []

    missing_items = {}
    missing_items["name"] = playlist_name
    missing_items["tracks"] = []

    for i in range(len(playlist_tracks)):
        print("\t{} - {}".format(i + 1, playlist_tracks[i]))
        search_results = ytmusic.search("{} {}".format(playlist_tracks[i]["Name"], playlist_tracks[i]["Artist"][0]), filter="songs", ignore_spelling=True)
        
        # append the tracks to the playlists_content tracks list
        playlist_contents["tracks"].append({"Name": playlist_tracks[i]["Name"], "Artist": playlist_tracks[i]["Artist"][0]})

        if search_results != []:
            search_result = search_results[0]
            print("\t\t YT Search: {} - {}".format(search_result['title'], search_result['artists'][0]['name']))

            try:
                ytmusic.add_playlist_items(playlist_id, [search_result['videoId']])

            except:
                print("Cannot add song - request timeout")
    
        else:
            print("\t\tCannot be found")
            missing_items["tracks"].append({"Name": playlist_tracks[i]["Name"], "Artist": playlist_tracks[i]["Artist"][0]})

    helpers.write_playlist_content(playlist_contents)
    helpers.write_playlist_content(missing_items, directory="./errors", missing_list=True)

    
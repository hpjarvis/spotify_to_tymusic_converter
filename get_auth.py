from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import uvicorn
import os
import signal
import json
import helpers
from datetime import datetime

secrets = helpers.load_secrets()
spotify_secrets = secrets['Spotify']

client_id = spotify_secrets['id']
client_secret = spotify_secrets['secret']
redirect_uri = "http://127.0.0.1:8000/callback"

app = FastAPI()

def get_access_token(auth_code: str):
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
        },
        auth=(client_id, client_secret),
    )

    data = response.json()
    data['timestamp'] = datetime.now().timestamp()

    return data

@app.get("/")
async def auth():
    scope = ["playlist-read-private", "playlist-read-collaborative"]
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={' '.join(scope)}"
    return HTMLResponse(content=f'<a href="{auth_url}">Authorize</a>')

@app.get("/callback")
async def callback(code):
    access_token = get_access_token(code)

    with open('./files/access_token.json', 'w') as f:
        json.dump(access_token, f, indent=4)
        print("Wrote auth code to file")
        print("Closing")

    os.kill(os.getpid(), signal.SIGINT)

    return "Done"

def run_auth_server():
    print("Open link to authorize app: http://127.0.0.1:8000")
    uvicorn.run(app, log_config=None)

if __name__ == "__main__":
    print("Open link to authorize app: http://127.0.0.1:8000")
    uvicorn.run(app, log_config=None)
"""
Author:         Mica Shatil
Date:           June 5, 2023
Inspiration:    https://www.youtube.com/watch?v=1TYyX8soQ8M&list=PLhYNDxVvF4oXa9ihs8WCzEriZsCF3Pp7A&index=3&ab_channel=JasonGoodison
Description:    This program will randomize the order of all spotify playlists whose IDs are in PLAYLIST_ID (see line 28)
                    and the owner of the playlists is the authorized user. 
"""
from flask import Flask, request, url_for, session, redirect
import os
from spotipy.oauth2 import SpotifyOAuth
import time
import requests
import random
import json
import signal
import webbrowser
import threading
import pyautogui

# App config
app = Flask(__name__)
app.secret_key = ""      # Fill in your secret key
app.config['SESSION_COOKIE_NAME'] = ""    # Fill in your session cookie name

# program constants
TOKEN_INFO = "token_info"
PLAYLIST_ID = []  # Playlist IDs to be modified... owner of these playlists will have to authorize the app
PROGRAM_FINISHED = False    # global var to denote whether the program has finished running and the tab can be closed

@app.route('/')
def login():
    """
    no need for homepage so you are instantly redirected to the spotify authorization url (which sends you back to redirectPage)
    """
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():
    """
    gets access token for user with required scope
    """
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect("/randomizePlaylist")

@app.route('/randomizePlaylist')
def randomizePlaylist():
    """
    modifies each playlist in PLAYLIST_ID to be in a random order
    """
    global PROGRAM_FINISHED

    for pl in PLAYLIST_ID:
        
        playlist = retrievePlaylist(pl)

        clearPlaylist(pl, playlist)
    
        playlist_filtered = [d["uri"] for d in playlist]
        
        random.shuffle(playlist_filtered)    # randomize the playlist order

        addToPlaylist(pl, playlist_filtered)

    PROGRAM_FINISHED = True
    return "DONE! WAIT FOR THIS TAB TO CLOSE"

def get_token():
    """
    Checks to see if token is valid and gets a new token if not
    """
    token_valid = False
    token_info = session.get(TOKEN_INFO, None)

    # Checking if the session already has a token stored
    if not (session.get(TOKEN_INFO, False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = token_info['expires_at'] - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    token_valid = True
    return token_info, token_valid

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),       # HARD CODE IF YOU TURN INTO EXE
        client_secret=os.getenv("CLIENT_SECRET"),       # HARD CODE IF YOU TURN INTO EXE
        redirect_uri=url_for('redirectPage', _external=True),
        scope="playlist-modify-private playlist-read-private playlist-read-collaborative playlist-modify-public"
    )

def get_auth_header(token):
    """
    token [string]

    format auth header correctly for spotify api
    """
    return {"Authorization": "Bearer " + str(token)}

def retrievePlaylist(playlistID):
    """
    playlistID [string]

    returns a list of the uris of all tracks in playlistID
    """
    token_info, authorized = get_token()
    if not authorized:
        return redirect('/')
    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    headers = get_auth_header(token_info["access_token"])
    query = f"?fields=items(track(uri))"
    limit = 100
    offset = 0
    results = []
    query_url = url + query
    tracks = []
    result = requests.get(query_url, params={"limit": limit, "offset": offset}, headers=headers)
    tracks = result.json()["items"]
    results.extend(tracks)
    offset += limit
    while len(tracks) == limit:  # actually get tracks from the api
        result = requests.get(query_url, params={"limit": limit, "offset": offset}, headers=headers)
        tracks = result.json()["items"]
        results.extend(tracks)
        offset += limit

    filtered_results = [d["track"] for d in results]   # filter tracks to return the uri for each only

    return filtered_results

def clearPlaylist(playlist_id, songs):
    """
    playlist_id [string] - playlist_id to clear
    songs [list of strings] - a list of key value pairs of the uri's of the songs to be cleared in the form [{"uri": *value of uri*}...]

    clears songs from playlist_id
    """
    token_info, authorized = get_token()
    if not authorized:
        return redirect('/')
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    header = get_auth_header(token_info["access_token"])
    header["Content-Type"] = "application/json"
    position = 0
    numTracks = len(songs)
    limit = min(100, numTracks)
    curURIs = songs[:limit]
    data2 = {"tracks": curURIs}
    args = {}
    args["data"] = json.dumps(data2)
    requests.delete(url, headers=header, **args)
    position += limit
    while position < numTracks:
        limit = min(100, numTracks - position)
        curURIs = songs[position:position+limit]
        data2 = {"tracks": curURIs}
        args = {}
        args["data"] = json.dumps(data2)
        requests.delete(url, headers=header, **args)
        position += limit
    
    return None

def addToPlaylist(playlist_id, songs):
    """
    playlist_id [string] - playlist_id to add the songs to
    songs [list of strings] - a list of the uri's of the songs to be added

    adds songs to playlist_id in the order they appear in songs
    """
    token_info, authorized = get_token()
    if not authorized:
        return redirect('/')
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    header = get_auth_header(token_info["access_token"])
    header["Content-Type"] = "application/json"
    position = 0
    numTracks = len(songs)
    limit = min(100, numTracks)
    curURIs = songs[:limit]
    data2 = {"uris": curURIs, "position": position}
    args = {}
    args["data"] = json.dumps(data2)
    requests.post(url, headers=header, **args)
    position += limit
    while position < numTracks:
        limit = min(100, numTracks - position)
        curURIs = songs[position:position+limit]
        data2 = {"uris": curURIs, "position": position}
        args = {}
        args["data"] = json.dumps(data2)
        requests.post(url, headers=header, **args)
        position += limit
    
    return None

def threadingFuncCallerJank():
    """
    opens the website to run the randomizer, waits for program to finish, closes the tab, and kills the program
    """
    global PROGRAM_FINISHED
    webbrowser.open_new("http://127.0.0.1:5000")    # open tab to start program
    while not PROGRAM_FINISHED:
        time.sleep(3)   # sleep for program to run
    pyautogui.hotkey('ctrlleft', 'w')   # close tab
    os.kill(os.getpid(), signal.SIGINT) # kill program
    
# run the script
if __name__ == "__main__":
    first_thread = threading.Thread(target=app.run)
    second_thread = threading.Thread(target=threadingFuncCallerJank)       # open the browser to authenticate and then run program
    first_thread.start()
    second_thread.start()

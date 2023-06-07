# Spotify-Playlisy-Shuffler
Spotify-Playlist-Shuffle is a template for a script that will randomize the order of a Spotify playlist. However, it was made for personal use so to make it work for you follow the steps in "Usage" below. The inspiration behind this is my hatred of spotify shuffle's lack of randomness.

# Usage
To use this program, the first step is to create a spotify developer app. You may follow the instructions here: https://developer.spotify.com/documentation/web-api/concepts/apps
Next, place the app key and secret in the .env file.
Additionally, you must fill in the app secret_key and session cookie name on lines 22 and 23 of app.py. These can be any values you wish to use.
The final step is to add the playlist IDs of the playlists you'd like to randomize into the list on line 27.
Now you can run the program and (with authorization) your playlist will be randomized.

Depending on your cookie settings, once you have authorized once your token and refresh tokens will be stored and so you will not need to sign in to authorize again. If your cookies allow for this you can then hardcode the values in your .env file into your program, and use pyinstaller to convert the program into and exe. Task Scheduler then allows you to set this program to run however frequently you'd like your playlist to be randomized.

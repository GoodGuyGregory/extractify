# Spotify Songs Exporter

I started this project to visualize the genres and artists I enjoy. I have dedicated many hours to studying, working, riding my bike to amazingly curated artists from Spotify. 
This project was designed to collect personal data from my library which is now termed "Liked_Songs" and I am not quite as happy about the change to a playlist focused development but I trust the platform and will continue to work through these updates. I started using spotify premium in 2015, and I've been waking up to an awesome Discover Weekly ever sense. 

I hope this project inspires you to interact with the spotify API and begin working with your own playlist curation and project ideas.

The Ultimate goal is to setup a Cogdb and Neo4J visualization of this data, more to come on this.


## Spotipy

in order to use spotipy's API client you will need to authorize an API through [Spotify's Dashboard](https://developer.spotify.com/dashboard) create an Application and follow the Quick Start [Authorization Code Flow from Spotipy](https://spotipy.readthedocs.io/en/2.24.0/index.html#authorization-code-flow). to spare you the jabber check out [this configuration video](https://www.youtube.com/watch?v=kaBVN8uP358&feature=youtu.be) 

there are two types of Spotipy Authorization Clients

## SpotifyOAuth Authorization

this is the prefered authorization if you're interested in user specific data. for the example here, I am pulling my `liked_songs` with this type of authorization. This is a highly rate limited version of the authentication and will cause all sorts of issues if your requests aren't limited to batches, or limited by pacing. ie setting a logically reasonable time between them the API police will rate limit you. 

I highly recommend using the `time` module along with `time.sleep(x)` to allow for a logical pace to prevent the request batches from getting flagged.

**Basic Configuration**

this is basically the gist of setting up a configuration with SpotifyOAuth. Remember to establish your client based on the callback function within the dashboard.
remember to establish a scope that makes sense for your project.

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])
```


## Client Credentials Authorization

this is used in server-to-server authorization and for for endpoints within the API that do not access user specific information. This allows for a larger request limit.

the basic configuration is the same. add a `.env` to allow for the `SPOTIFY_CLIENT_ID` and the `SPOTIFY_CLIENT_SECRET`to allow for the `SpotifyClientCredentials` to connect successfully.

**Basic Configuration**

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = sp.user_playlists('spotify')
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
```


## Getting An Artist's Genre

[Common Complaint](https://stackoverflow.com/questions/61624487/extract-artist-genre-and-song-release-date-using-spotipy)

## Documentation

[Spotify Dashboard](https://developer.spotify.com/dashboard)
[Spotipy](https://spotipy.readthedocs.io/en/2.24.0/)

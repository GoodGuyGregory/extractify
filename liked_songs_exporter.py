import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv


def checkConnection(sp):
    try:
        # check connection 
        gorillaz_uri = 'spotify:artist:3AA28KZvwAUcZuOKwyblJQ'

        results = sp.artist_albums(gorillaz_uri, album_type='album')
        albums = results['items']
        
        print("Connection Succesfull:")

        print("Gorillaz Albums:")
        print("----------------------------------")

        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])

        for album in albums:
            print(album['name'])
    except Exception as e:
        print(f"Something went wrong with Spotify Authorization: {e}")

def get_artists(artists_list):
    artists = ''
    
    if len(artists_list) == 1:
        artists += artists_list[0]['name']
        return artists

    for i in range(len(artists_list)):
        artist_name = artists_list[i]['name']
        artists += artist_name  + ', '

        if i == len(artists_list - 1):
            artists += artist_name 
        
    return artists



def calc_duration_ms(duration_ms):
    minute_conversion = duration_ms / 1000 / 60
    minute_total = round(minute_conversion, 2)
    return str(minute_total).replace('.',':')

def get_artist_genre(sp, spotify_external_url, spotify_album_url):
    artist = sp.artist(spotify_external_url)
    if len(artist['genres']) == 0:
        # check the album genre:
        album = sp.album(spotify_album_url)
        return album['genres']
    else:
        return artist['genres']

def get_album_release_year(sp, spotify_external_url):
    album = sp.album(spotify_external_url)
    return album['release_date']
    
def main():
    # load the client variables
    load_dotenv()

    client_id = os.getenv('APP_CLIENT_ID')

    spotify_app_client_secret = os.getenv("SPOTIFY_APP_CLIENT_SECRET")

    spotify_app_redirect = os.getenv("SPOTIFY_APP_REDIRECT_URI")


    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=spotify_app_client_secret,
                                                redirect_uri=spotify_app_redirect,
                                                scope=["user-library-read","playlist-modify-private"]))

    results = sp.current_user_saved_tracks()
    
    current_user = sp.current_user()
    
    print('Current User Details:' )
    print('-------------------------------------------')
    print(f'User Name: {current_user['display_name']}' )
    print(f'Total Liked Songs: {results['total']}')

    saved_tracks = results['items']
    
    print("Last Liked Track:")
    print("------------------------------")
    print(f'Song Name: {saved_tracks[0]['track']['name']}')
    print(f'Length: {calc_duration_ms(saved_tracks[0]['track']['duration_ms'])}')
    print(f'Album Name: {saved_tracks[0]['track']['album']['name']}')
    print(f'Artists: {get_artists(saved_tracks[0]['track']['artists'])}')
    
    song_artist_url = saved_tracks[0]['track']['artists'][0]['external_urls']['spotify']
    album_url = saved_tracks[0]['track']['album']['external_urls']['spotify']
    
    print(f'Genre: {get_artist_genre(sp, song_artist_url, album_url)}')
    print(f'Release Date: {get_album_release_year(sp, album_url)}')
    
    


main()
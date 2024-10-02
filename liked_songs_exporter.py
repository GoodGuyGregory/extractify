import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pandas as pd
import sys
import requests
import time


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
    
    else:
        
        for i in range(len(artists_list)):
            artist_name = artists_list[i]['name']
            if i == len(artists_list) - 1:
                if artist_name not in artists:
                    artists += artist_name 
            else:
                artists += artist_name  + ', '        
        
    return artists


def parse_tracks(sp_clients, saved_track_data, saved_tracks):

    for i in range(len(saved_tracks)):
        song_name = saved_tracks[i]['track']['name']
        
        length = calc_duration_ms(saved_tracks[i]['track']['duration_ms'])
        
        album_name = saved_tracks[i]['track']['album']['name']
        
        artists = get_artists(saved_tracks[i]['track']['artists'])

        song_artist_url = saved_tracks[i]['track']['artists'][0]['external_urls']['spotify']
        
        artist_id = song_artist_url.split('/')[-1]

        album_id = album_url.split('/')[-1]
        

        # adds the song details into dictionary
        saved_track_data['Song Name'].append(song_name)
        
        saved_track_data['Duration'].append(length)
        
        saved_track_data['Album'].append(album_name)
        
        saved_track_data['Artists'].append(artists)

        saved_track_data['Artist_id'].append(artist_id)

        saved_track_data['Album_id'].append(album_id)
        
    

def calc_duration_ms(duration_ms):
    minute_conversion = duration_ms / 1000 / 60
    minute_total = round(minute_conversion, 2)
    return str(minute_total).replace('.',':')



def export_track_data(saved_tracks, user_name):
    df = pd.DataFrame(saved_tracks)

    file_name = user_name + '_liked_songs_with_artist_genre.csv'

    df.to_csv(file_name, index=False)

def main():
    # load the client variables
    load_dotenv()

    client_id = os.getenv('APP_CLIENT_ID')

    spotify_app_client_secret = os.getenv("SPOTIFY_APP_CLIENT_SECRET")

    spotify_app_redirect = os.getenv("SPOTIFY_APP_REDIRECT_URI")


    user_sp_client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=spotify_app_client_secret,
                                                redirect_uri=spotify_app_redirect,
                                                scope=["user-library-read","playlist-modify-private"]
                                                ),requests_timeout=30)

    api_sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                                                        client_id=client_id,
                                                        client_secret=spotify_app_client_secret,
                                                        ),requests_timeout=30)
    
    sp_clients = { 'user_sp': user_sp_client, 'api_sp': api_sp_client}

    # checkConnection(sp_clients['user_sp'])
    # time.sleep(10)
    # checkConnection(sp_clients['api_sp'])
    # time.sleep(10)

    results = user_sp_client.current_user_saved_tracks()
    
    current_user = user_sp_client.current_user()
    
    print('Current User Details:' )
    print('-------------------------------------------')
    print(f'User Name: {current_user['display_name']}' )
    print(f'Total Liked Songs: {results['total']}')

    total_num_saved = results['total']

    saved_tracks_data = {
        'Song Name': [],
        'Duration': [],
        'Album': [],
        'Artists': [],
        'Artist_id': [], 
        'Album_id': [],

    }

    offset_index = 0
    while offset_index != total_num_saved:
        results = sp_clients['user_sp'].current_user_saved_tracks(limit=25, offset=offset_index)
        
        total_saved_tracks = results['items']

        sys.stdout.write(f'\rLoading Song Data... {round(((offset_index+25)/total_num_saved)*100)}%')
        
        parse_tracks(sp_clients=sp_clients, saved_track_data=saved_tracks_data, saved_tracks=total_saved_tracks)
        time.sleep(5)
        sys.stdout.flush()

        # control offset increase:
        if (offset_index + 25) < total_num_saved:
            offset_index += 25
        else:
            # determine the difference to offset
            if (offset_index + 25) > total_num_saved:
                offset_index = (total_num_saved - offset_index) + offset_index


    print('\n--------------------------------')
    print('\nExporting Complete!')
    print('--------------------------------')
    print('Exporting Liked Songs')
    user_name = current_user['display_name'].replace(' ', '_')
    export_track_data(saved_tracks=saved_tracks_data, user_name=user_name )
    
main()